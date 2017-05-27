from fnmatch import fnmatch

import hexchat

__module_name__ = "ZNC-snofilter"
__module_version__ = "0.0.1"
__module_description__ = "Companion script to my snofilter module for ZNC, moves all notices from the module in to query windows"

def get_net_name():
    for ctx in hexchat.get_list('channels'):
        if ctx.type == 1 and ctx.network == hexchat.get_info('network'):
            return ctx.channel


def handle(word, word_eol, event):
    if not fnmatch(word[0], "*!snofilter@znc.in"):
        return hexchat.EAT_NONE
    window = word[0].split('!', 1)[0][2:].lower()
    net = "{}-snotices".format(get_net_name())
    serv = hexchat.find_context(net)
    if not serv:
        hexchat.command("newserver -noconnect {}".format(net))
        serv = hexchat.find_context(net)
    serv.command("query -nofocus {}".format(window))
    window_ctx = hexchat.find_context(net, window)
    window_ctx.emit_print(event, window, word_eol[3][1:])
    return hexchat.EAT_HEXCHAT


def on_notice(word, word_eol, userdata):
    return handle(word, word_eol, "Notice")


def on_privmsg(word, word_eol, userdata):
    return handle(word, word_eol, "Private Message to Dialog")

hexchat.hook_unload(lambda userdata: print(__module_name__, "plugin unloaded"))

hexchat.hook_server("NOTICE", on_notice)
hexchat.hook_server("PRIVMSG", on_privmsg)
print(__module_name__, "plugin loaded.")
