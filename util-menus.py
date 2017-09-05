import hexchat

__module_name__ = "UtilMenus"
__module_author__ = "linuxdaemon"
__module_version__ = "0.1.0"
__module_description__ = "Adds various menu options for general util functions"

MENU_ITEMS = frozenset({
    ("$NICK/Services Info", "NS info %s"),
    ("$CHAN/Services Info", "CS info %s"),
    ("$TAB/Services Info", "CS info %s"),
})


def add_menu_items():
    for path, cmd in MENU_ITEMS:
        hexchat.command("MENU ADD \"{}\" \"{}\"".format(path, cmd))


def del_menu_items():
    for path, cmd in MENU_ITEMS:
        hexchat.command("MENU DEL \"{}\"".format(path))


def unload(userdata):
    del_menu_items()
    print(__module_name__, "plugin unloaded")


hexchat.hook_unload(unload)
add_menu_items()

print(__module_name__, "plugin loaded")
