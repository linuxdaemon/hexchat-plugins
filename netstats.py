# coding=utf-8
import asyncio
from functools import partial
from operator import itemgetter, attrgetter
from statistics import mean
from threading import Thread
from typing import Tuple, Sequence, TYPE_CHECKING

import hexchat

if TYPE_CHECKING:
    from hexchat import WordList

__module_name__ = "NetStats"
__module_author__ = "linuxdaemon"
__module_version__ = "0.1.0"
__module_description__ = "Network Statistics"

LOOP = asyncio.get_event_loop()
FORMATS = {}


def stats_format(name):
    def _decorate(func):
        FORMATS[name] = func
        return func

    return _decorate


@stats_format("full")
def stats_full(max_users, max_chans, context):
    network = context.get_info("network")
    channels = {
        chan.channel: chan.context.get_list("users")
        for chan in context.get_list("channels")
        if chan.network == network and chan.type == 2
    }

    yield "User counts:"
    yield from (
        "    {}: {}".format(channel, len(users))
        for channel, users in channels.items()
    )
    yield "Average: {} users per channel".format(
        round(mean(map(len, channels.values())), 3)
    )


@stats_format("brief")
def stats_brief(max_users, max_chans, context):
    network = context.get_info("network")
    channels = {
        chan.channel: chan.context.get_list("users")
        for chan in context.get_list("channels")
        if chan.network == network and chan.type == 2
    }
    visible_users = set()
    for users in channels.values():
        visible_users.update(map(attrgetter("nick"), users))

    parts = (
        ("channels", (len(channels), max_chans, "member of")),
        ("users", (len(visible_users), max_users, "share a channel with"))
    )

    def _get_data(part: Tuple[str, Tuple[int, int, str]]):
        name, (count, total, desc) = part
        return {
            "name": name.title(),
            "desc": desc,
            "num": count,
            "max": total,
            "percent": round((count / total) * 100, 2),
        }

    part_text = "{name}: {max} ({desc} {num} [{percent}%])"
    msg = "Global stats: {} Average {} users per channel".format(
        ' '.join(
            part_text.format_map(_get_data(part)) for part in parts
        ),
        round(mean(map(len, channels.values())), 2)
    )
    return msg,


def handle_raw(future: 'asyncio.Future'):
    def _handler(word, word_eol, userdata):
        LOOP.call_soon_threadsafe(future.set_result, word)

    return _handler


@asyncio.coroutine
def await_numeric(numeric):
    fut = LOOP.create_future()
    hook = hexchat.hook_server(numeric, handle_raw(fut))
    line = yield from fut
    hexchat.unhook(hook)
    return line


@asyncio.coroutine
def get_stats(context: 'hexchat.Context', args: Sequence[str]):
    args = list(args)
    say = False
    _stats_format = "brief"
    while args:
        arg = args.pop(0)
        if arg == "-o":
            say = True
        else:
            _stats_format = arg
            args.clear()

    if _stats_format not in FORMATS:
        print("No handler exists for format '{}'".format(_stats_format))
        return

    formatter = FORMATS[_stats_format]
    LOOP.call_later(0.5, context.command, "LUSERS")

    numerics = {
        "chans": ("254", 3),
        "users": ("266", 6),
    }

    lines = yield from asyncio.gather(
        *map(await_numeric, map(itemgetter(0), numerics.values())), loop=LOOP
    )

    data = {
        name: int(line[pos])
        for line in lines
        for name, (numeric, pos) in numerics.items()
        if line[1] == numeric
    }

    args = (data["users"], data["chans"], context)

    if asyncio.iscoroutine(formatter) or \
            asyncio.iscoroutinefunction(formatter):
        msg = yield from formatter(*args)
    else:
        msg = formatter(*args)

    for line in (msg or ()):
        if say:
            context.command("say {}".format(line))
        else:
            context.prnt(line)


def stats_cmd(word: 'WordList', word_eol: 'WordList', userdata):
    context = hexchat.find_context(
        hexchat.get_info("network"), hexchat.get_info("channel")
    )
    LOOP.call_soon_threadsafe(
        partial(asyncio.ensure_future, loop=LOOP),
        get_stats(context, word[1:])
    )
    return hexchat.EAT_ALL


def unload(userdata):
    LOOP.call_soon_threadsafe(LOOP.stop)
    print(__module_name__, "plugin unloaded")


hexchat.hook_unload(unload)

hexchat.hook_command(
    "NETSTATS", stats_cmd,
    help="NETSTATS [-o] [{}], returns statistics for the user on the current "
         "network. If the -o flag is set, then the output is sent to the "
         "current channel".format('|'.join(FORMATS.keys()))
)

Thread(name="loop-thread", target=LOOP.run_forever).start()
print(__module_name__, "plugin loaded")
