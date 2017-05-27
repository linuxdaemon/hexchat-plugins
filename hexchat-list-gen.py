# coding=utf-8
"""
Used to generate the type hint list items in hexchat.py
"""
from typing import Tuple

TYPES = {
    'i': 'int',
    't': 'int',  # Time
    'p': None,  # "pointer" (object instance in Python)
    's': 'str',
}

# Hardcoded mapping of types for pointer fields
PTR_TYPES = {
    'context': 'Context'
}

"""
Field lists from 
https://github.com/hexchat/hexchat/blob/master/src/common/plugin.c#L1342-L1364
"""
dcc_fields = (
    "iaddress32", "icps", "sdestfile", "sfile", "snick", "iport", "ipos",
    "iposhigh", "iresume", "iresumehigh", "isize", "isizehigh", "istatus",
    "itype"
)

channels_fields = (
    "schannel", "schannelkey", "schanmodes", "schantypes", "pcontext",
    "iflags", "iid", "ilag", "imaxmodes", "snetwork", "snickmodes",
    "snickprefixes", "iqueue", "sserver", "itype", "iusers"
)

ignore_fields = ("iflags", "smask")

notify_fields = ("iflags", "snetworks", "snick", "toff", "ton", "tseen")

users_fields = (
    "saccount", "iaway", "shost", "tlasttalk", "snick", "sprefix",
    "srealname", "iselected"
)

FIELD_LISTS = (
    ('DCC', dcc_fields),
    ('Channel', channels_fields),
    ('Ignore', ignore_fields),
    ('Notify', notify_fields),
    ('User', users_fields),
)


def get_field_type(field: str) -> Tuple[str, str]:
    type_char = field[0]
    field = field[1:]
    assert type_char in TYPES
    type_hint = TYPES[type_char]
    if not type_hint:
        assert field in PTR_TYPES
        return field, PTR_TYPES[field]
    return field, type_hint


def format_fields(fields, indent_level=0, indent_size=4):
    indent = ' ' * indent_size * indent_level
    return [
        "{indent}('{field}', {type}),".format(
            indent=indent, field=field, type=field_type
        )
        for field, field_type in map(get_field_type, fields)
    ]


def generate_list(name, fields):
    lines = [
        "{name}ListItem = NamedTuple(",
        "    '{name}ListItem',",
        "    [",
        *format_fields(fields, indent_level=2),
        "    ]",
        ")",
    ]
    return [line.format(name=name) for line in lines]


def generate():
    lines = []
    for list_name, fields in FIELD_LISTS:
        lines.extend(generate_list(list_name, fields))
        lines.append('')
    lists = ["{name}List".format(name=name) for name, _ in FIELD_LISTS]
    lines.extend(
        "{list} = List[{list}Item]".format(list=name) for name in lists
    )
    lines.append('')
    lines.append("Lists = Union[{}]".format(', '.join(lists)))
    lines.append('')
    print('\n'.join(lines))

if __name__ == "__main__":
    generate()
