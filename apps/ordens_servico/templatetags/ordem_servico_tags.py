from django import template

register = template.Library()

@register.filter
def has_attr(obj, attr):
    """Verifica se um objeto tem um determinado atributo"""
    return hasattr(obj, attr)
