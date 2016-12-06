import hexchat
import time

__module_name__ = "DayTurnover"
__module_version__ = "0.1"
__module_description__ = "Adds a 'Day changed' message to buffers on day turnovers"

# CAVEATS
# This module only announces day changes whenever any raw line has been received, 
# so if no activity occurs for a whole day, a turnover message may not be broadcast

old_day = None
day_format = "%d %b %Y"


def on_data(word, word_eol, userdata, attributes):
    global old_day
    day = time.localtime(attributes.time or time.time())[:3]
    if old_day and old_day == day:
        return hexchat.EAT_NONE
    
    old_day = day
    for chan in hexchat.get_list("channels"):
        chan.context.prnt("Day changed to {}".format(time.strftime(day_format, day)))
    return hexchat.EAT_NONE


def unload(userdata):
    print(__module_name__, "plugin unloaded")


hexchat.hook_server_attrs("RAW LINE", on_data)
hexchat.hook_unload(unload)

print(__module_name__, "plugin loaded")
