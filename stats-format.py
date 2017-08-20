# coding=utf-8
import operator
import time
from collections import namedtuple

import hexchat

__module_name__ = "StatsFormat"
__module_author__ = "linuxdaemon"
__module_version__ = "0.1.0"
__module_description__ = "Formats the output from /stats for g/z/e/k/q-lines for InspIRCd"

NETWORKS = {
    "snoonet",
    "snoodev",
}

STATS_END = '219'

LINE_FMT = "\2{name}\2: {mask} \2set at\2: {set_time} \2by\2: {source} " \
           "\2duration\2: {duration} \2expires\2: {expires} " \
           "\2reason\2: {reason}"

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
    StatHandler(name='A:Line', numeric='210', char='a'),
    StatHandler(name='CBAN', numeric='210', char='C'),
    StatHandler(name='E:Line', numeric='223', char='e'),
    StatHandler(name='G:Line', numeric='223', char='g'),
    StatHandler(name='GA:Line', numeric='210', char='A'),
    StatHandler(name='SHUN', numeric='223', char='H'),
    StatHandler(name='K:Line', numeric='216', char='k'),
    StatHandler(name='Q:Line', numeric='217', char='q'),
    StatHandler(name='R:Line', numeric='223', char='R'),
    StatHandler(name='SVSHOLD', numeric='210', char='S'),
    StatHandler(name='Z:Line', numeric='223', char='Z'),
)

HOOKS = dict()


def get_net_ctx():
    for ctx in hexchat.get_list('channels'):
        if ctx.type == 1 and ctx.network == hexchat.get_info('network'):
            return ctx


def time_format(seconds: int, perm: str) -> str:
    ts = ""
    for char, divisor in TIME_MULTIPLIERS:
        value, seconds = divmod(seconds, divisor)
        if value:
            ts += "{}{}".format(value, char)
    return ts or perm


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
        expires_at = (set_time + duration) if duration else 0
        expires_in = int(expires_at - time.time())
        if expires_in < 0:
            expires_in = 0
        if reason[0] == ':':
            reason = reason[1:]
        data = {
            'name': stat.name,
            'mask': displayable,
            'set_time': time.ctime(set_time),
            'source': source,
            'duration': time_format(duration, 'permanent'),
            'expires': time_format(expires_in, 'never'),
            'reason': reason,
        }
        get_net_ctx().context.prnt(LINE_FMT.format_map(data))
        return hexchat.EAT_HEXCHAT

    return _handle


def on_stats_end(word, word_eol, userdata):
    for hook in HOOKS.values():
        hexchat.unhook(hook)
    HOOKS.clear()


def stats_cmd(word, word_eol, userdata):
    if get_net_ctx().channel.lower() in NETWORKS:
        char = word[1]
        HOOKS.update({
            stat.char: hexchat.hook_server(
                stat.numeric, stat_handler(stat)
            )
            for stat in STATS if stat.char == char
        })
        HOOKS[STATS_END] = hexchat.hook_server(STATS_END, on_stats_end)


hexchat.hook_unload(lambda userdata: print(__module_name__, "plugin unloaded"))

hexchat.hook_command('STATS', stats_cmd)

print(__module_name__, "plugin loaded")
