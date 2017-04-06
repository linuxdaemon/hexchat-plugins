import os
import sys

import hexchat

sys.path = [os.path.join(hexchat.get_info("configdir"), "addons")] + sys.path

from libhex import hook

__module_name__ = "NotificationClear"
__module_description__ = "Clears all notifications in all contexts"
__module_version__ = "0.1"


@hook.command("CLEARNOTIF")
def clear(word, word_eol, userdata):
    for chan in hexchat.get_list("channels"):
        chan.context.command("GUI COLOR 0")

    return hexchat.EAT_ALL


@hook.unload
def unload(userdata):
    print(__module_name__, "plugin unloaded")


print(__module_name__, "plugin loaded")
