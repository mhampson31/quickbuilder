from django import template

import re

register = template.Library()

rgx = re.compile(r'\[([\w\s]+?)\]')

icon_text = {
    'Barrel Roll':'barrelroll',
    'Bank Left':'bankleft',
    'Bank Right':'bankright',
    'Bullseye Arc':'bullseyearc',
    'Single Turret Arc':'singleturretarc',
    'Critical Hit':'crit',
    'Front Arc':'frontarc',
    'Force Power':'forcepower',
    'Force Charge':'forcecharge',
    'Rear Arc':'reararc',
    'Rotate Arc':'rotatearc',
    'Tallon Roll Left':'trollleft',
    'Tallon Roll Right':'trollright',
    'Turn Left':'turnleft',
    'Turn Right':'turnright'
}

def regex_icon(m):
    return get_icon(m[1])


@register.filter(is_safe=True)
def get_icon(iname, css=''):
    if ' ' in iname:
        iname = icon_text.get(iname, iname)
    iname = iname.lower()
    """Returns the <i> block that inserts an icon from the xwing font css. Doesn't work for ship icons."""
    return '<i class="xwing-miniatures-font xwing-miniatures-font-{} {}"></i>'.format(iname, css)



@register.filter(is_safe=True)
def iconize(text):
    return re.sub(rgx, regex_icon, text)

