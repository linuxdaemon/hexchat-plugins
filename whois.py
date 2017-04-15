import threading
from collections import namedtuple

import dns.resolver
import ipwhois
import re

import hexchat

__module_name__ = "WHOISLookup"
__module_description__ = "Provides commands to look up an IP address in whois and check it against DNSBLs"
__module_version__ = "0.1.0"

IP_RE = re.compile(r"^[0-9]{1,3}(?:\.[0-9]{1,3}){3}$")
THREADS = []
DNSBLS = [
    "dnsbl.sorbs.net",
    "spam.dnsbl.sorbs.net",
    "tor.dnsbl.sectoor.de",
    "rbl.efnetrbl.org",
    "tor.efnet.org",
    "zen.spamhaus.org",
    "dnsbl.dronebl.org",
    "torexit.dan.me.uk",
    "dnsbl.tornevall.org",
]


class Thread(threading.Thread):
    def __init__(self, target, *args, **kwargs):
        super().__init__(target=target, args=args, **kwargs)
        self.start()


def get_query(name, server=None):
    query = hexchat.find_context(server=server, channel=name)
    if not query:
        hexchat.command("query -nofocus {}".format(name))
        query = hexchat.find_context(server=server, channel=name)

    return query


def do_whois(ip, ctx, nick=None):
    serv = ctx.get_info("network")
    query = get_query(">>whois-lookup<<", serv)
    try:
        wi = ipwhois.IPWhois(ip)
        data = wi.lookup_rdap()
        net = data.get("network", {})
        netname = net.get("name")
        cidr = net.get("cidr")
        names = [obj["contact"]["name"] for obj in data.get("objects", []).values()
                 if "contact" in obj and "name" in obj["contact"]]

        name = "UNKNOWN"
        if len(names) > 0:
            name = names[0]

        pfx = ""
        if nick:
            pfx = "{nick} is logged in from ".format(nick=nick)

        data = {"pfx": pfx, "ip": ip, "contact": name, "netname": netname, "cidr": cidr}
        msg = "{pfx}IP '{ip}', owned by {contact} ({netname} {cidr})".format(**data)
        fmsg = "{pfx}IP '{ip}' ({netname} {cidr})".format(**data)
        query.prnt(msg)
        ctx.command("say WHOIS DATA: {}".format(fmsg))

    except ipwhois.exceptions.IPDefinedError as e:
        query.prnt("{} is reserved".format(ip))


DNSResp = namedtuple('DNSResp', 'blacklist record text')


def check_dnsbl(ip):
    for bl in DNSBLS:
        resolv = dns.resolver.Resolver()
        query = "{}.{}".format(".".join(reversed(ip.split("."))), bl)  # d.c.b.a.blacklist
        try:
            ans = resolv.query(query, "A")
            txt = resolv.query(query, "TXT")
            yield DNSResp(bl, ans[0], txt[0])

        except dns.resolver.NXDOMAIN:
            pass


def do_dnsbl(ip, ctx, nick=None):
    if not IP_RE.match(ip):
        return

    matches = list(check_dnsbl(ip))

    if nick:
        ip = "{} ({})".format(ip, nick)

    query = get_query(">>dnsbl-lookup<<", ctx.get_info("network"))

    msg = "[DNSBL] IP: {ip} is listed in {bl} ({rec}: {txt})"
    msg1 = msg + " and {num} other{plural}"

    for i in range(len(matches)):
        match = matches[i]
        data = {"ip": ip, "bl": match.blacklist, "rec": match.record, "txt": match.text, "num": len(matches) - 1,
                "plural": "s" if len(matches) > 2 else ""}

        if i == 0:
            ctx.command("say " + (msg1 if len(matches) > 1 else msg).format(**data))

        query.prnt(msg.format(**data))


def lookup(args):
    global THREADS
    chan = hexchat.get_info("channel")
    net = hexchat.get_info("network")
    if not args or chan.lower() not in ["#staff", "##sysop", "##sherlock", "##ldtest"]:
        return

    ctx = hexchat.find_context(net, chan)

    for ip in args:
        THREADS.append(Thread(do_whois, ip, ctx, name="WHOIS-{}".format(ip)))
        THREADS.append(Thread(do_dnsbl, ip, ctx, name="DNSBL-{}".format(ip)))


def cull_threads(userdata):
    i = 0
    while i < len(THREADS):
        if not THREADS[i].is_alive():
            del THREADS[i]
        else:
            i += 1

    return True


commands = {"$lookup": lookup}


def cmd_cb(word, word_eol, userdata):
    text = word[1]
    if text[0] == ':':
        text = text[1:]

    args = text.split()
    if not args:
        return hexchat.EAT_NONE

    cmd = args.pop(0)
    if cmd.lower() not in commands:
        return hexchat.EAT_NONE

    commands[cmd.lower()](args)

    return hexchat.EAT_NONE


@hexchat.hook_unload
def unload_cb(userdata):
    print(__module_name__, "plugin unloaded")


hexchat.hook_print("Channel Message", cmd_cb)
hexchat.hook_print("Your Message", cmd_cb)
hexchat.hook_timer(300000, cull_threads)

print(__module_name__, "plugin loaded")
