from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Safely grab dictionary[key] or return None.
    Usage in template: {{ some_dict|get_item:some_key }}
    """
    try:
        return dictionary.get(key)
    except Exception:
        return None
