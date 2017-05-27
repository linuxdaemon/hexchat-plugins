# coding=utf-8
import hexchat

__module_name__ = "NetStats"
__module_description__ = "Network Statistics"
__module_version__ = "0.1.0"

HOOK_NAME_FMT = "{cmd}_{func.__name__}"
HOOKS = dict()
data = dict()


def on_global_chans(word, word_eol, userdata):
    net = hexchat.get_info("network").lower()
    if data.get(net, {}).get("enabled"):
        data[net]["numchannels"] = int(word[3])
        check_state(net)


def on_user_count(word, word_eol, userdata):
    net = hexchat.get_info("network").lower()
    if data.get(net, {}).get("enabled"):
        data[net]["numusers"] = int(word[6])
        check_state(net)


DATA_HOOKS = (
    ("254", on_global_chans),
    ("266", on_user_count),
)


def check_state(net):
    if "state" not in data[net]:
        data[net]["state"] = 0

    data[net]["state"] += 1
    if data[net]["state"] > 1:
        data[net]["state"] = 0
        print_stats(data[net])
        del data[net]


def print_stats(netdata):
    netdata["enabled"] = False
    ctx = netdata["ctx"]
    network = ctx.get_info("network")

    visiblechans = [
        chan for chan in ctx.get_list("channels")
        if chan.network == network and chan.type == 2
    ]
    visibleusers = set(
        user.nick for chan in visiblechans
        for user in chan.context.get_list("users")
    )

    numchans = len(visiblechans)
    numusers = len(visibleusers)

    maxchans = netdata["numchannels"]
    maxusers = netdata["numusers"]

    fmt_data = {
        "numchans": numchans,
        "maxchans": maxchans,
        "pctchans": (numchans / maxchans) * 100,
        "numusers": numusers,
        "maxusers": maxusers,
        "pctusers": (numusers / maxusers) * 100,
    }

    fmt = "Global stats: Channels: {maxchans} (member of {numchans} " \
          "[{pctchans:.2g}%]) Users: {maxusers} (share a channel with " \
          "{numusers} [{pctusers:.2g}%])"

    if netdata.get("say"):
        ctx.command("say {}".format(fmt.format(**fmt_data)))
    else:
        ctx.prnt(fmt.format(**fmt_data))


def enable_hooks():
    for cmd, func in DATA_HOOKS:
        name = HOOK_NAME_FMT.format(cmd=cmd, func=func)
        assert name not in HOOKS, "Attempt to reregister existing hooks"
        HOOKS[name] = hexchat.hook_server(cmd, func)


def disable_hooks():
    for cmd, func in DATA_HOOKS:
        name = HOOK_NAME_FMT.format(cmd=cmd, func=func)
        assert name in HOOKS, "Attempt to deregister non-existant hooks"
        hexchat.unhook(HOOKS[name])


def stats_cmd(word, word_eol, userdata):
    net = hexchat.get_info("network")
    data[net.lower()] = {
        "ctx": hexchat.find_context(net, hexchat.get_info("channel")),
        "say": "-o" in word[1:],
        "enabled": True
    }

    hexchat.command("LUSERS")
    return hexchat.EAT_ALL


hexchat.hook_unload(lambda userdata: print(__module_name__, "plugin unloaded"))

hexchat.hook_command(
    "NETSTATS", stats_cmd, help="NETSTATS [-o], returns statistics for the "
                                "user on the current network. "
                                "If the -o flag is set, then the output is "
                                "sent to the current channel"
)

print(__module_name__, "plugin loaded")
