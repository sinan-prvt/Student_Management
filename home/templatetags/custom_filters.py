from django import template

register = template.Library()

@register.filter
def split(value, key):
    if not value:
        return []
    return [v.strip() for v in value.split(key)]