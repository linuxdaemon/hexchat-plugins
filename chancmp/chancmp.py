import hexchat

__module_name__ = "Chan Compare"
__module_description__ = "Compares User Lists Between Channels"
__module_version__ = "0.0.1"


DIALOG_FMT = ">>{name}<<"  # produces '>>test<<' as a query dialog
wi_watch = {}


def wprint(w, line):
    w.emit_print("Private Message to Dialog", "hexchat", line, "")


def get_window(name):
    wname = DIALOG_FMT.format(name=name)
    c = hexchat.find_context(channel=wname)
    if not c:
        hexchat.command("query -nofocus {}".format(wname))
        c = hexchat.find_context(channel=wname)

    return c


def cmp_cb(word, wordeol, userdata):
    w = get_window("chancmp")
    runs = 0
    match_nicks = []
    found_nicks = []
    wprint(w, "Searching for common users in: {}".format(",".join(word[1:])))
    for chan in word[1:]:
        found_nicks = []
        ctx = hexchat.find_context(channel=chan)
        for user in ctx.get_list("users"):
            if runs == 0:
                match_nicks.append(user.nick)
            else:
                found_nicks.append(user.nick)

        if runs != 0:
            match_nicks = set(found_nicks) & set(match_nicks)

        runs += 1

    wprint(w, "{}".format(match_nicks))
    return hexchat.EAT_ALL


def find_cb(word, word_eol, userdata):
    w = get_window("nickfind")
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


def whois_cb(word, word_eol, userdata):
    nick = word[3]
    if nick in wi_watch and hexchat.get_info("network") in wi_watch[nick]["networks"]:
        wprint(wi_watch[nick]["ctx"], "Found {} on {}".format(nick, hexchat.get_info("network")))


def endwhois_cb(word, word_eol, userdata):
    if word[3] in wi_watch and hexchat.get_info("network") in wi_watch[word[3]]["networks"]:
        wi_watch[word[3]]["networks"].remove(hexchat.get_info("network"))


def find1_cb(word, word_eol, userdata):
    w = get_window("srvfind")
    for nick in word[1:]:
        wprint(w, "Searching all servers for (may take a while): {}".format(nick))
        wi_watch[nick] = {}
        wi_watch[nick]["ctx"] = w
        wi_watch[nick]["networks"] = []
        for ctx in hexchat.get_list("channels"):
            if ctx.type == 1:
                wi_watch[nick]["networks"].append(ctx.network)
                ctx.context.command("WHOIS {}".format(nick))

    return hexchat.EAT_ALL


@hexchat.hook_unload
def unload_cb(userdata):
    print(__module_name__, "plugin unloaded")


hexchat.hook_command("CHANCMP", cmp_cb, help="Compare the user lists of provided channels")
hexchat.hook_command("NICKFIND", find_cb, help="Find which contexts a user is visible in")
hexchat.hook_command("SRVFIND", find1_cb, help="find which servers/networks a user is visible on")
hexchat.hook_server("311", whois_cb)
hexchat.hook_server("318", endwhois_cb)

print(__module_name__, "plugin loaded")

