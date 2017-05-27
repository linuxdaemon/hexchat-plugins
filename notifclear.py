# coding=utf-8
import hexchat

__module_name__ = "NotificationClear"
__module_description__ = "Clears all notifications in all contexts"
__module_version__ = "0.1.0"


def clear(word, word_eol, userdata):
    for chan in hexchat.get_list("channels"):
        chan.context.command("GUI COLOR 0")

    return hexchat.EAT_ALL


hexchat.hook_unload(lambda userdata: print(__module_name__, "plugin unloaded"))
hexchat.hook_command(
    "CLEARNOTIF", clear,
    help="Clear all context highlights, setting them back to the default tab "
         "color"
)

print(__module_name__, "plugin loaded")
