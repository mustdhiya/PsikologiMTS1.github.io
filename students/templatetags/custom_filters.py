# students/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='replace')
def replace(value, args):
    """
    Replace occurrences of a substring in a string
    Usage: {{ text|replace:"old,new" }}
    """
    if args:
        search, replace_with = args.split(',')
        return value.replace(search, replace_with)
    return value

@register.filter(name='format_category_name')
def format_category_name(value):
    """
    Format category name by replacing underscores with spaces and title case
    Usage: {{ category|format_category_name }}
    """
    return value.replace('_', ' ').title()


@register.filter
def multiply(value, arg):
    """Multiply value by arg"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0