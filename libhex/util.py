import hexchat


def get_query(server=None, name=None):
    query = hexchat.find_context(server=server, channel=name)
    if not query:
        hexchat.command("query -nofocus {}".format(name))
        query = hexchat.find_context(server=server, channel=name)

    return query
