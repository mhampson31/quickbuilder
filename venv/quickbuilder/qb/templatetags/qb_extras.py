from django import template

register = template.Library()

@register.filter(is_safe=True)
def get_icon(iname, css=None):
    return '<i class="xwing-miniatures-font xwing-miniatures-font-{} {}"></i>'.format(iname, css if css else '')
