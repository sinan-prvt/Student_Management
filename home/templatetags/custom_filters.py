from django import template

register = template.Library()

@register.filter
def split(value, key):
    """Split a string by the given key and strip spaces"""
    if not value:
        return []
    return [v.strip() for v in value.split(key)]