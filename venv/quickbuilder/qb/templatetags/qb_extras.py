from django import template

import re

register = template.Library()

tag_regex = re.compile(r'\[(.+)\]')


def regex_icon(m):
    return get_icon(m[1])


@register.filter(is_safe=True)
def get_icon(iname, css=''):
    """Returns the <i> block that inserts an icon from the xwing font css. Doesn't work for ship icons."""
    iname = iname.lower().strip(' ')
    return '<i class="xwing-miniatures-font xwing-miniatures-font-{} {}"></i>'.format(iname, css)



@register.filter(is_safe=True)
def iconize(text):
    return re.sub(tag_regex, regex_icon, text)

