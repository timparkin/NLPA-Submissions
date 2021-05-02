from django.utils.safestring import mark_safe

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def limit_length_tooltip(value):
    if len(value)>40:
        limitvalue = "%s...%s"%(value[:20], value[-20:])
        return mark_safe('<span data-bs-toggle="tooltip" data-bs-placement="top" title="%s">%s</span>'%(value,limitvalue))

    else:
        return value
