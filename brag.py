# coding=utf-8
import threading
from collections import Counter
from threading import Thread

import hexchat

__module_name__ = "Brag"
__module_author__ = "linuxdaemon"
__module_version__ = "0.1.0"
__module_description__ = "Adds a /BRAG command"

statuses = ["o:line", "op", "halfop", "voice"]

prefix_types = {
    "~": "op",
    "&": "op",
    "!": "op",
    "@": "op",
    "%": "halfop",
    "+": "voice",
}

usermodes = {}
remaining_umodes = 0
umode_event = threading.Event()


def get_status_level(prefix, prefixes="@%+"):
    if not prefix:
        return 0
    return prefixes[::-1].index(prefix) + 1


def brag(context):
    networks = {}
    network_contexts = []
    for chan in hexchat.get_list("channels"):
        if chan.type == 1 and chan.context.get_info("server") is not None:
            network_contexts.append(chan.context)
        elif chan.type == 2:
            status_prefixes = chan.nickprefixes
            user_prefixes = {
                user.nick:
                    (user.prefix,
                     get_status_level(user.prefix, status_prefixes))
                for user in chan.context.get_list("users")
            }

            my_status, my_level = user_prefixes[chan.context.get_info("nick")]
            lower_users = []
            for nick, (prefix, level) in user_prefixes.items():
                if level < my_level:
                    lower_users.append(nick)

            networks.setdefault(chan.network, {})[chan.channel] = {
                "prefix": my_status,
                "lower_users": lower_users,
            }

    num_channels = sum(len(channels) for channels in networks.values())
    msg = "I'm on {} channels across {} networks".format(
        num_channels, len(networks.keys())
    )
    counts = Counter(
        prefix_types[chan["prefix"]]
        for channels in networks.values()
        for chan in channels.values()
        if chan["prefix"]
    )
    global remaining_umodes
    remaining_umodes = len(network_contexts)
    umode_event.clear()
    umode_hook = hexchat.hook_server("221", umode)
    for ctx in network_contexts:
        ctx.command("quote MODE {}".format(ctx.get_info("nick")))

    if umode_event.wait(5):
        counts["o:line"] = 0
        for modes in usermodes.values():
            if "o" in modes:
                counts["o:line"] += 1

    hexchat.unhook(umode_hook)
    umode_event.clear()

    parts = [
        "{} {}{}".format(
            counts[status], status,
            "s" if counts[status] > 1 else ""
        )
        for status in sorted(counts.keys(), key=statuses.index)
        if status
    ]
    if len(parts) > 1:
        parts[-1] = "and {}".format(parts[-1])

    delim = ", " if len(parts) > 2 else " "
    power = {}
    for network, channels in networks.items():
        for channel in channels.values():
            power.setdefault(network, set()).update(channel["lower_users"])

    msg += ", I have " + delim.join(parts) + " with power over {} users" \
        .format(sum(len(users) for users in power.values()))

    context.command("say {}".format(msg))


def umode(word, word_eol, userdata):
    global remaining_umodes
    if word[2] == hexchat.get_info("nick"):
        remaining_umodes -= 1
        usermodes[hexchat.get_info("network")] = word[3]
        if remaining_umodes == 0:
            umode_event.set()


def brag_cmd(word, word_eol, userdata):
    Thread(target=brag, args=[hexchat.get_context()], daemon=True).start()
    return hexchat.EAT_ALL


hexchat.hook_unload(lambda userdata: print(__module_name__, "plugin unloaded"))

hexchat.hook_command("BRAG", brag_cmd)

print(__module_name__, "plugin load")
