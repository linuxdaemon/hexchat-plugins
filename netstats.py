import os
import sys

import hexchat

sys.path = [os.path.join(hexchat.get_info("configdir"), "addons")] + sys.path

from libhex import hook

__module_name__ = "NetStats"
__module_description__ = "Network Statistics"
__module_version__ = "0.0.2"

data = {}


@hook.server("254")
def on_global_chans(word, word_eol, userdata):
    net = hexchat.get_info("network").lower()
    if data.get(net, {}).get("enabled"):
        data[net]["numchannels"] = int(word[3])
        check_state(net)


@hook.server("266")
def on_user_count(word, word_eol, userdata):
    net = hexchat.get_info("network").lower()
    if data.get(net, {}).get("enabled"):
        data[net]["numusers"] = int(word[6])
        check_state(net)


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

    visiblechans = [chan for chan in ctx.get_list("channels") if chan.network == network and chan.type == 2]
    visibleusers = set(user.nick for chan in visiblechans for user in chan.context.get_list("users"))

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

    fmt = "Global stats: Channels: {maxchans} (member of {numchans} [{pctchans:.2g}%]) " \
          "Users: {maxusers} (share a channel with {numusers} [{pctusers:.2g}%])"

    if netdata.get("say"):
        ctx.command("say {}".format(fmt.format(**fmt_data)))
    else:
        print(fmt.format(**fmt_data))


@hook.command("NETSTATS")
def stats_cmd(word, word_eol, userdata):
    net = hexchat.get_info("network")
    data[net.lower()] = {
        "ctx": hexchat.find_context(net, hexchat.get_info("channel")),
        "say": "-o" in word[1:],
        "enabled": True
    }

    hexchat.command("LUSERS")
    return hexchat.EAT_ALL


@hook.unload
def unload(userdata):
    print(__module_name__, "plugin unloaded")


print(__module_name__, "plugin loaded")
