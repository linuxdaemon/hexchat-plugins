from typing import Any

import hexchat


def command(name: str, userdata: Any = None, priority: int = hexchat.PRI_NORM, help: str = None):
    return lambda func: hexchat.hook_command(name, func, userdata=userdata, priority=priority, help=help)


def server(name: str, userdata: Any = None, priority: int = hexchat.PRI_NORM):
    return lambda func: hexchat.hook_server(name, func, userdata=userdata, priority=priority)


def unload(func):
    hexchat.hook_unload(func)
