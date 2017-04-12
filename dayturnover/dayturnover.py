import datetime
import os
import sys

import hexchat

sys.path = [os.path.join(hexchat.get_info("configdir"), "addons")] + sys.path

from libhex import hook

__module_name__ = "DayTurnover"
__module_version__ = "0.0.2"
__module_description__ = "Adds a 'Day changed' message to buffers on day turnovers"

DEFAULT_FMT = "Day changed to %d %b %Y"
DEFAULT_INTERVAL = 30

timer_hook = None
state = 0


def getpref(name, default):
    val = hexchat.get_pluginpref("{}_{}".format(__module_name__.lower(), name.lower()))
    return val if val is not None else default


def setpref(name, value):
    return hexchat.set_pluginpref("{}_{}".format(__module_name__.lower(), name.lower()), value)


def timer_cb(userdata):
    global state
    now = datetime.datetime.now()
    if now.hour == 23 and now.minute == 59:
        state = 1
    elif now.hour == 0 and now.minute == 0 and state == 1:
        state = 2
        for chan in hexchat.get_list("channels"):
            chan.context.prnt(now.strftime(getpref("format", DEFAULT_FMT)))

    return True


def enable(word, word_eol):
    setpref("enabled", True)
    global timer_hook
    if timer_hook is None:
        timer_hook = hexchat.hook_timer(getpref("interval", DEFAULT_INTERVAL) * 1000, timer_cb)
        print(__module_name__, "enabled")
    else:
        print(__module_name__, "already enabled")


def disable(word, word_eol):
    setpref("enabled", False)
    global timer_hook
    if timer_hook is not None:
        hexchat.unhook(timer_hook)
        timer_hook = None
        print(__module_name__, "disabled")
    else:
        print(__module_name__, "not enabled")


def fmt(word, word_eol):
    if word_eol and word_eol[0]:
        if not setpref("format", word_eol[0]):
            print("Failed to set format")
            return

    print(__module_name__, "format:", getpref("format", DEFAULT_FMT))


def interval(word, word_eol):
    if word and word[0]:
        intv = int(word[0])
        if not setpref("interval", intv):
            print("Failed to set interval")
            return

    print(__module_name__, "interval:", getpref("interval", DEFAULT_INTERVAL), "seconds")


commands = {
    "on": enable,
    "off": disable,
    "format": fmt,
    "interval": interval,
}


@hook.command("DAYCHANGE", help="DAYCHANGE [ON|OFF|FORMAT <format string>|INTERVAL <seconds>]")
def cmd_cb(word, word_eol, userdata):
    if len(word) < 2:
        hexchat.command("HELP {}".format(word[0]))
    else:
        subcmd = word[1].lower()
        if subcmd in commands:
            commands[subcmd](word[2:], word_eol[2:])
        else:
            hexchat.command("HELP {}".format(word[0]))

    return hexchat.EAT_ALL


@hook.unload
def unload(userdata):
    print(__module_name__, "plugin unloaded")


if getpref("enabled", True):
    timer_hook = hexchat.hook_timer(getpref("interval", DEFAULT_INTERVAL) * 1000, timer_cb)

print(__module_name__, "plugin loaded")
