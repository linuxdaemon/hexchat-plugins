# coding=utf-8
import hexchat

__module_name__ = "Chan Compare"
__module_author__ = "linuxdaemon"
__module_version__ = "0.1.0"
__module_description__ = "Compares User Lists Between Channels"

DIALOG_FMT = ">>{name}<<"  # produces '>>test<<' as a query dialog
wi_watch = {}


def get_query(name, server=None):
    name = DIALOG_FMT.format(name=name)
    hexchat.command("query -nofocus {}".format(name))
    return hexchat.find_context(server=server, channel=name)


def wprint(w, line):
    w.emit_print("Private Message to Dialog", "hexchat", line, "")


def cmp_cb(word, wordeol, userdata):
    w = get_query("chancmp")
    first = True
    match_nicks = set()
    wprint(w, "Searching for common users in: {}".format(",".join(word[1:])))
    for chan in word[1:]:
        ctx = hexchat.find_context(channel=chan)
        found_nicks = set(user.nick for user in ctx.get_list("users"))
        if first:
            first = False
            match_nicks = found_nicks
        else:
            match_nicks &= found_nicks

    wprint(w, "{}".format(match_nicks))
    return hexchat.EAT_ALL


def find_cb(word, word_eol, userdata):
    w = get_query("nickfind")
    for nick in word[1:]:
        wprint(w, "Searching for: {}".format(nick))
        data = {}
        for chan in w.get_list("channels"):
            for user in chan.context.get_list("users"):
                if nick == user.nick:
                    data.setdefault(chan.network, []).append(chan.channel)

        for net in data:
            wprint(w, "{}: {}".format(net, ", ".join(data[net])))

    return hexchat.EAT_ALL


def srvfind(word, word_eol, userdata):
    w = get_query("srvfind")
    for nick in word[1:]:
        wprint(
            w, "Searching all servers for (may take a while): {}".format(nick)
        )
        wi_watch[nick] = {
            "ctx": w,
            "networks": []
        }

        for ctx in hexchat.get_list("channels"):
            if ctx.type == 1:
                wi_watch[nick]["networks"].append(ctx.network)
                ctx.context.command("WHOIS {}".format(nick))

    return hexchat.EAT_ALL


def whois_cb(word, word_eol, userdata):
    nick = word[3]
    net = hexchat.get_info("network")
    if nick in wi_watch and net in wi_watch[nick]["networks"]:
        wprint(
            wi_watch[nick]["ctx"], "Found {} on {}".format(nick, net)
        )


def endwhois_cb(word, word_eol, userdata):
    if word[3] in wi_watch and hexchat.get_info("network") in \
            wi_watch[word[3]]["networks"]:
        wi_watch[word[3]]["networks"].remove(hexchat.get_info("network"))


hexchat.hook_unload(lambda userdata: print(__module_name__, "plugin unloaded"))

hexchat.hook_command(
    "CHANCMP", cmp_cb, help="Compare the user lists of provided channels"
)
hexchat.hook_command(
    "NICKFIND", find_cb, help="Find which contexts a user is visible in"
)
hexchat.hook_command(
    "SRVFIND", srvfind, help="find which servers/networks a user is visible on"
)

hexchat.hook_server("311", whois_cb)
hexchat.hook_server("318", endwhois_cb)

print(__module_name__, "plugin loaded")
