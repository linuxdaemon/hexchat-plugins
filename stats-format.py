# coding=utf-8
import operator
import time
from collections import namedtuple

import hexchat

__module_name__ = "StatsFormat"
__module_version__ = "0.0.1"
__module_description__ = "Formats the output from /stats for g/z/e/k/q-lines for InspIRCd"

NETWORKS = {
    "snoonet",
    "snoodev"
}

LINE_FMT = "{name}: {mask} set at {set_time} by {source} \2duration\2: {duration} \2reason\2: {reason}"

TIME_MULTIPLIERS = (
    ('y', 365 * 24 * 60 * 60),
    ('w', 7 * 24 * 60 * 60),
    ('d', 24 * 60 * 60),
    ('h', 60 * 60),
    ('m', 60),
    ('s', 1),
)

StatHandler = namedtuple('StatHandler', 'name numeric char')

STATS = (
    StatHandler('CBAN', '210', 'C'),
    StatHandler('E:Line', '223', 'e'),
    StatHandler('G:Line', '223', 'g'),
    StatHandler('SHUN', '223', 'H'),
    StatHandler('K:Line', '216', 'k'),
    StatHandler('Q:Line', '217', 'q'),
    StatHandler('R:Line', '223', 'R'),
    StatHandler('SVSHOLD', '210', 'S'),
    StatHandler('Z:Line', '223', 'Z'),
)

HOOKS = dict()


def get_net_ctx():
    for ctx in hexchat.get_list('channels'):
        if ctx.type == 1 and ctx.network == hexchat.get_info('network'):
            return ctx


def time_format(seconds: int) -> str:
    ts = ""
    for char, divisor in TIME_MULTIPLIERS:
        value, seconds = divmod(seconds, divisor)
        if value:
            ts += "{}{}".format(value, char)
    return ts or "permanent"


def stat_handler(stat: StatHandler):
    def _handle(word, word_eol, userdata):
        line = word_eol[3]
        if line[0] == ':':
            line = line[1:]
        # {displayable} {set_time} {duration} {source} :{reason}
        if operator.countOf(line, ' ') < 4:
            return
        displayable, set_time, duration, source, reason = line.split(None, 4)
        set_time = int(set_time)
        duration = int(duration)
        if reason[0] == ':':
            reason = reason[1:]
        get_net_ctx().context.prnt(
            LINE_FMT.format(
                name=stat.name, mask=displayable,
                set_time=time.ctime(set_time), source=source,
                duration=time_format(duration), reason=reason
            )
        )
        return hexchat.EAT_HEXCHAT

    return _handle


def on_stats_end(word, word_eol, userdata):
    for hook in HOOKS.values():
        hexchat.unhook(hook)


def stats_cmd(word, word_eol, userdata):
    if get_net_ctx().channel.lower() == 'snoonet':
        char = word[1]
        for stat in STATS:
            if stat.char == char:
                HOOKS[stat.char] = hexchat.hook_server(
                    stat.numeric, stat_handler(stat)
                )


hexchat.hook_unload(lambda userdata: print(__module_name__, "plugin unloaded"))

hexchat.hook_command('STATS', stats_cmd)
hexchat.hook_server('219', on_stats_end)
print(__module_name__, "plugin loaded")
