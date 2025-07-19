from django import template

register = template.Library()

@register.filter
def get_item(mapping, key):
    """Lookup mapping[key] (returns [] if missing)."""
    return mapping.get(key, [])
