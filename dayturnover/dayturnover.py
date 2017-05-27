# coding=utf-8
import datetime
from typing import Sequence, Dict, Tuple, Callable, Optional, TypeVar

import hexchat

__module_name__ = "DayTurnover"
__module_version__ = "0.1.0"
__module_description__ = "Adds a 'Day changed' message to buffers on day turnovers"

WordList = Sequence[Optional[str]]
CommandCallback = Callable[[WordList, WordList], None]
Func = TypeVar('Func')
CmdDecoReturn = Callable[[Func], Func]

DEFAULT_FMT = "Day changed to %d %b %Y"
DEFAULT_INTERVAL = 30

timer_hook = None
state = 0
commands = dict()  # type: Dict[str, Tuple[CommandCallback, int]]


def getpref(name, default):
    val = hexchat.get_pluginpref("{}_{}".format(__module_name__, name))
    if val is None:
        return default
    return val


def setpref(name, value):
    return hexchat.set_pluginpref("{}_{}".format(__module_name__, name), value)


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


def start_timer():
    global timer_hook
    assert timer_hook is None, \
        "Attempted to start timer that was already running"
    timer_hook = hexchat.hook_timer(
        getpref("interval", DEFAULT_INTERVAL) * 1000, timer_cb
    )


def stop_timer():
    global timer_hook
    assert timer_hook is not None, \
        "Attempted to stop timer that wasn't running"
    hexchat.unhook(timer_hook)
    timer_hook = None


def command(*names: str, min_args: int = 0) -> CmdDecoReturn:
    def _command(func: Func):
        for name in names:
            commands[name] = (name, min_args)
        return func

    return _command


@command("on", "enable")
def enable(word: Sequence[str], word_eol: Sequence[str]) -> None:
    setpref("enabled", True)
    if timer_hook is None:
        start_timer()
        print(__module_name__, "enabled")
    else:
        print(__module_name__, "already enabled")


@command("off", "disable")
def disable(word: Sequence[str], word_eol: Sequence[str]) -> None:
    setpref("enabled", False)
    global timer_hook
    if timer_hook is not None:
        stop_timer()
        print(__module_name__, "disabled")
    else:
        print(__module_name__, "not enabled")


@command("format")
def fmt(word: Sequence[str], word_eol: Sequence[str]) -> None:
    if word_eol and word_eol[0]:
        if not setpref("format", word_eol[0]):
            print("Failed to set format")
            return

    print(__module_name__, "format:", getpref("format", DEFAULT_FMT))


@command("interval")
def interval(word: Sequence[str], word_eol: Sequence[str]) -> None:
    if word and word[0]:
        try:
            intv = float(word[0])
        except ValueError:
            print("Invalid interval value")
            return

        if not setpref("interval", intv):
            print("Failed to set interval")
            return

        if timer_hook is not None:
            stop_timer()
            start_timer()

    print(
        __module_name__, "interval:", getpref("interval", DEFAULT_INTERVAL),
        "seconds"
    )


def cmd_cb(word, word_eol, userdata):
    if len(word) < 2:
        hexchat.command("HELP {}".format(word[0]))
    else:
        subcmd = word[1].lower()
        if subcmd in commands:
            # TODO support min_args properly
            commands[subcmd][0](word[2:], word_eol[2:])
        else:
            hexchat.command("HELP {}".format(word[0]))

    return hexchat.EAT_ALL


hexchat.hook_unload(lambda userdata: print(__module_name__, "plugin unloaded"))
hexchat.hook_command(
    "DAYCHANGE", cmd_cb,
    help="DAYCHANGE [ON|OFF|FORMAT <format string>|INTERVAL <seconds>]"
)

if getpref("enabled", True):
    start_timer()

print(__module_name__, "plugin loaded")
