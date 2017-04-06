"""
Dummy hexchat interface
"""
from typing import Union, List, Callable, Any

PRI_HIGHEST = 127
PRI_HIGH = 64
PRI_NORM = 0
PRI_LOW = (-64)
PRI_LOWEST = (-128)

EAT_NONE = 0
EAT_HEXCHAT = 1
EAT_PLUGIN = 2
EAT_ALL = (EAT_HEXCHAT | EAT_PLUGIN)

__version__ = (2, 12)


def prnt(s: str) -> None:
    pass


def emit_print(event_name: str, *args) -> None:
    pass


def command(s: str) -> None:
    pass


def nickcmp(s1: str, s2: str) -> int:
    pass


def strip(text: str, length: int = -1, flags: int = 3) -> str:
    pass


def get_info(t: str) -> Union[str, None]:
    pass


def get_prefs(name: str) -> str:
    pass


def get_list(t: str) -> list:
    pass


def hook_command(name: str, callback: Callable, userdata: Any = None, priority: int = PRI_NORM,
                 help: str = None) -> Any:
    pass


def hook_print(name: str, callback: Callable, userdata: Any = None, priority: int = PRI_NORM) -> Any:
    pass


def hook_print_attrs(name: str, callback: Callable, userdata: Any = None, priority: int = PRI_NORM) -> Any:
    pass


def hook_server(name: str, callback: Callable, userdata: Any = None, priority: int = PRI_NORM) -> Any:
    pass


def hook_server_attrs(name: str, callback: Callable, userdata: Any = None, priority: int = PRI_NORM) -> Any:
    pass


def hook_timer(timeout: int, callback: Callable, userdata: Any = None) -> Any:
    pass


def hook_unload(callback: Callable, userdata: Any = None) -> Any:
    pass


def unhook(handler):
    pass


def set_pluginpref(name: str, value: Any) -> bool:
    pass


def get_pluginpref(name: str) -> Union[str, int, None]:
    pass


def del_pluginpref(name: str) -> bool:
    pass


def list_pluginpref() -> List[str]:
    pass


class Context:
    def __init__(self):
        pass

    def set(self):
        pass

    def prnt(self, s: str):
        pass

    def emit_print(self, event_name: str, *args):
        pass

    def command(self, string: str):
        pass

    def get_info(self, type: str) -> str:
        pass

    def get_list(self, type: str) -> List:
        pass


def get_context() -> Context:
    pass


def find_context(server: str = None, channel: str = None) -> Context:
    pass
