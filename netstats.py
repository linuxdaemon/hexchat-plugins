import hexchat

__module_name__ = "NetStats"
__module_description__ = "Network Statistics"
__module_version__ = "0.1"


data = {}


def on254(word, word_eol, userdata):
    net = hexchat.get_info("network").lower()
    if data.get(net, {}).get("enabled"):
        data.setdefault(net, {})["numchannels"] = int(word[3])
        if "state" not in data[net]:
            data[net]["state"] = 0

        data[net]["state"] += 1
        if data[net]["state"] > 1:
            data[net]["state"] = 0
            print_stats(data[net])


def on266(word, word_eol, userdata):
    net = hexchat.get_info("network").lower()
    if data.get(net, {}).get("enabled"):
        data.setdefault(net, {})["numusers"] = int(word[6])
        if "state" not in data[net]:
            data[net]["state"] = 0

        data[net]["state"] += 1
        if data[net]["state"] > 1:
            data[net]["state"] = 0
            print_stats(data[net])


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
            "pctchans": (numchans / maxchans)*100,
            "numusers": numusers,
            "maxusers": maxusers,
            "pctusers": (numusers / maxusers)*100,
            }

    fmt = "Global stats: Channels: {maxchans} (member of {numchans} [{pctchans:.2g}%]) Users: {maxusers} (share a channel with {numusers} [{pctusers:.2g}%])"
    
    if netdata.get("say"):
        ctx.command("say " + fmt.format(**fmt_data))
    else:
        print(fmt.format(**fmt_data))


def stats_cmd(word, word_eol, userdata):
    net = hexchat.get_info("network")
    data[net.lower()] = {
            "ctx": hexchat.find_context(net, hexchat.get_info("channel")),
            "say": len(word) > 1 and "-o" in word[1:],
            "enabled": True
        }

    hexchat.command("LUSERS")
    return hexchat.EAT_ALL


@hexchat.hook_unload
def unload(userdata):
    print(__module_name__, "plugin unloaded")


hexchat.hook_command("NETSTATS", stats_cmd)
hexchat.hook_server("254", on254)
hexchat.hook_server("266", on266)

print(__module_name__, "plugin loaded")

