# core/templatetags/filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Safe dictionary lookup — works even if dictionary is None or not a dict
    """
    if isinstance(dictionary, dict):
        return dictionary.get(str(key))
    return None  # or "" or "—"