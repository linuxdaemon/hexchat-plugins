# coding=utf-8
"""
Dummy hexchat interface
"""

from typing import Union, List, Callable, Optional, TypeVar, NamedTuple

PRI_HIGHEST = 127
PRI_HIGH = 64
PRI_NORM = 0
PRI_LOW = (-64)
PRI_LOWEST = (-128)

EAT_NONE = 0
EAT_HEXCHAT = 1
EAT_PLUGIN = 2
EAT_ALL = (EAT_HEXCHAT | EAT_PLUGIN)

WordList = List[Optional[str]]
T = TypeVar('T')

__version__ = (1, 0)


class Context:
    def __init__(self) -> None: ...

    def set(self) -> None: ...

    def command(self, string: str) -> None: ...

    def prnt(self, s: str) -> None: ...

    def emit_print(self, name: str, arg1: str = None, arg2: str = None,
                   arg3: str = None, arg4: str = None, arg5: str = None,
                   arg6: str = None, time: int = None) -> int: ...

    def get_info(self, type: str) -> Optional[str]: ...

    def get_list(self, type: str) -> 'Lists': ...


Attribute = NamedTuple('Attribute', [('time', int)])

# Code generated from hexchat-list-gen.py
DCCListItem = NamedTuple(
    'DCCListItem',
    [
        ('address32', int),
        ('cps', int),
        ('destfile', str),
        ('file', str),
        ('nick', str),
        ('port', int),
        ('pos', int),
        ('poshigh', int),
        ('resume', int),
        ('resumehigh', int),
        ('size', int),
        ('sizehigh', int),
        ('status', int),
        ('type', int),
    ]
)

ChannelListItem = NamedTuple(
    'ChannelListItem',
    [
        ('channel', str),
        ('channelkey', str),
        ('chanmodes', str),
        ('chantypes', str),
        ('context', Context),
        ('flags', int),
        ('id', int),
        ('lag', int),
        ('maxmodes', int),
        ('network', str),
        ('nickmodes', str),
        ('nickprefixes', str),
        ('queue', int),
        ('server', str),
        ('type', int),
        ('users', int),
    ]
)

IgnoreListItem = NamedTuple(
    'IgnoreListItem',
    [
        ('flags', int),
        ('mask', str),
    ]
)

NotifyListItem = NamedTuple(
    'NotifyListItem',
    [
        ('flags', int),
        ('networks', str),
        ('nick', str),
        ('off', int),
        ('on', int),
        ('seen', int),
    ]
)

UserListItem = NamedTuple(
    'UserListItem',
    [
        ('account', str),
        ('away', int),
        ('host', str),
        ('lasttalk', int),
        ('nick', str),
        ('prefix', str),
        ('realname', str),
        ('selected', int),
    ]
)

DCCList = List[DCCListItem]
ChannelList = List[ChannelListItem]
IgnoreList = List[IgnoreListItem]
NotifyList = List[NotifyListItem]
UserList = List[UserListItem]

Lists = Union[DCCList, ChannelList, IgnoreList, NotifyList, UserList]


# End of generated code


def command(s: str) -> None: ...


def prnt(s: str) -> None: ...


def emit_print(name: str, arg1: str = None, arg2: str = None, arg3: str = None,
               arg4: str = None, arg5: str = None, arg6: str = None,
               time: int = None) -> int: ...


def get_info(t: str) -> Optional[str]: ...


def get_prefs(name: str) -> Union[str, int, None]: ...


def get_context() -> Optional['Context']: ...


def find_context(server: str = None, channel: str = None) -> \
        Optional['Context']: ...


def set_pluginpref(name: str, value: Union[str, int]) -> bool: ...


def get_pluginpref(name: str) -> Union[str, int, None]: ...


def del_pluginpref(name: str) -> bool: ...


def list_pluginpref() -> List[str]: ...


def hook_command(name: str,
                 callback: Callable[[WordList, WordList, T], Optional[int]],
                 userdata: T = None, priority: int = PRI_NORM,
                 help: str = None) -> int: ...


def hook_server(name: str,
                callback: Callable[[WordList, WordList, T], Optional[int]],
                userdata: T = None, priority: int = PRI_NORM) -> int: ...


def hook_server_attrs(name: str,
                      callback: Callable[[WordList, WordList, T, Attribute],
                                         Optional[int]],
                      userdata: T = None, priority: int = PRI_NORM) -> int: ...


def hook_print(name: str,
               callback: Callable[[WordList, WordList, T],
                                  Optional[int]],
               userdata: T = None, priority: int = PRI_NORM) -> int: ...


def hook_print_attrs(name: str,
                     callback: Callable[[WordList, WordList, T, Attribute],
                                        Optional[int]],
                     userdata: T = None, priority: int = PRI_NORM) -> int: ...


def hook_timer(timeout: int, callback: Callable[[T], bool],
               userdata: T = None) -> int: ...


def hook_unload(callback: Callable[[T], None], userdata: T = None) -> int: ...


def unhook(handler: Union[str, int]) -> None: ...


def get_list(t: str) -> 'Lists': ...


def get_lists() -> List[str]: ...


def nickcmp(s1: str, s2: str) -> int: ...


def strip(text: str, length: int = -1, flags: int = 3) -> str: ...
