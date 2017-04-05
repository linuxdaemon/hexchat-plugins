import hexchat

__module_name__ = "NotificationClear"
__module_description__ = "Clears all notifications in all contexts"
__module_version__ = "0.1"


def clear(word, word_eol, userdata):
    for chan in hexchat.get_list("channels"):
        chan.context.command("GUI COLOR 0")

    return hexchat.EAT_ALL


@hexchat.hook_unload
def unload(userdata):
    print(__module_name__, "plugin unloaded")


hexchat.hook_command("CLEARNOTIF", clear)
print(__module_name__, "plugin loaded")

