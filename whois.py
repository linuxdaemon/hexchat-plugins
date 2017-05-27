# coding=utf-8
import re
import threading
from collections import namedtuple
from typing import Tuple, Generator

import dns.resolver
import hexchat
import ipwhois

__module_name__ = "WHOISLookup"
__module_description__ = "Provides commands to look up an IP address in whois and check it against DNSBLs"
__module_version__ = "0.2.0"

IP_RE = re.compile(r"^[0-9]{1,3}(?:\.[0-9]{1,3}){3}$")
THREADS = list()
DNSBLS = {
    "dnsbl.sorbs.net",
    "spam.dnsbl.sorbs.net",
    "tor.dnsbl.sectoor.de",
    "rbl.efnetrbl.org",
    "tor.efnet.org",
    "zen.spamhaus.org",
    "dnsbl.dronebl.org",
    "torexit.dan.me.uk",
    "dnsbl.tornevall.org",
}
CHANS = {"#staff", "##sysop", "##sherlock", "##ldtest"}
RESOLVER = dns.resolver.Resolver()


class Thread(threading.Thread):
    def __init__(self, target, *args, **kwargs):
        super().__init__(target=target, args=args, **kwargs)
        self.start()


def pluralize(count: int, unit: str):
    if count == 1:
        return "{} {}".format(count, unit)
    return "{} {}s".format(count, unit)


def get_query(name: str, server: str = None) -> 'hexchat.Context':
    hexchat.command("query -nofocus {}".format(name))
    return hexchat.find_context(server=server, channel=name)


def do_whois(ip: str, ctx: 'hexchat.Context', nick: str = None) -> None:
    server = ctx.get_info("network")
    query = get_query(">>whois-lookup<<", server)
    try:
        whois = ipwhois.IPWhois(ip)
        result = whois.lookup_rdap()
        net = result.get("network", {})
        netname = net.get("name")
        cidr = net.get("cidr")
        names = []
        objects = result.get("objects", {})
        for obj in objects.values():
            name = obj.get("contact", {}).get("name")
            if name:
                names.append(name)

        name = "UNKNOWN"
        if names:
            name = names[0]

        prefix = "{nick} is logged in from".format(nick=nick) if nick else ""
        data = {
            "prefix": prefix,
            "ip": ip,
            "contact": name,
            "netname": netname,
            "cidr": cidr,
        }
        log_msg = "{prefix}IP '{ip}', owned by {contact} ({netname} {cidr})"
        chan_msg = "[WHOIS] {prefix}IP '{ip}' ({netname} {cidr})"
        query.prnt(log_msg.format_map(data))
        ctx.command("say {}".format(chan_msg).format_map(data))

    except ipwhois.IPDefinedError:
        query.prnt("{} is reserved".format(ip))


DNSResp = namedtuple('DNSResp', 'blacklist record text')


def check_dnsbl(ip: str) -> Generator[DNSResp, None, None]:
    for bl in DNSBLS:
        # d.c.b.a.blacklist
        query = "{}.{}".format('.'.join(reversed(ip.split('.'))), bl)
        try:
            ans = RESOLVER.query(query, "A")
            txt = RESOLVER.query(query, "TXT")
            yield DNSResp(bl, ans[0], txt[0])

        except dns.resolver.NXDOMAIN:
            pass


def do_dnsbl(ip: str, ctx: 'hexchat.Context', nick: str = None) -> None:
    if not IP_RE.match(ip):
        return

    matches = list(check_dnsbl(ip))
    if not matches:
        return

    if nick:
        ip = "{} ({})".format(ip, nick)

    query = get_query(">>dnsbl-lookup<<", ctx.get_info("network"))
    log_msg = "IP: {ip} is listed in {match.blacklist} " \
              "({match.record}: {match.text})"
    suffix = ""
    if len(matches) > 2:
        suffix = " and {}".format(pluralize(len(matches) - 1, "count"))
    ctx.command(
        "say [DNSBL] " + log_msg.format(ip=ip, match=matches[0]) + suffix
    )

    for match in matches:
        query.prnt(log_msg.format(ip=ip, match=match))


LOOKUPS = (
    ("WHOIS", do_whois),
    ("DNSBL", do_dnsbl),
)


def run_lookup(ip: str, ctx: 'hexchat.Context'):
    for name, func in LOOKUPS:
        Thread(func, ip, ctx, name="{}-{}".format(name, ip))


def lookup(args: Tuple[str]):
    chan = hexchat.get_info("channel")
    if chan.lower() not in CHANS:
        return

    net = hexchat.get_info("network")
    ctx = hexchat.find_context(net, chan)
    for ip in args:
        run_lookup(ip, ctx)


def cull_threads(userdata) -> bool:
    for thread in reversed(THREADS):
        if not thread.is_alive():
            THREADS.remove(thread)

    return True


COMMANDS = {"$lookup": lookup}


def cmd_cb(word, word_eol, userdata):
    text = word[1]
    if text[0] == ':':
        text = text[1:]

    args = text.split()
    if args:
        cmd, *args = args
        if cmd.lower() in COMMANDS:
            COMMANDS[cmd.lower()](args)
    return hexchat.EAT_NONE


def lookup_cmd(word, word_eol, userdata):
    if len(word) == 1:
        hexchat.command("HELP {}".format(word[0]))
    else:
        lookup(word[1:])
    return hexchat.EAT_ALL


hexchat.hook_unload(lambda userdata: print(__module_name__, "plugin unloaded"))

hexchat.hook_command(
    "LOOKUP", lookup_cmd, help="LOOKUP <IP address>{, <IP address>}"
)
hexchat.hook_print("Channel Message", cmd_cb)
hexchat.hook_print("Your Message", cmd_cb)
hexchat.hook_timer(300000, cull_threads)

print(__module_name__, "plugin loaded")
