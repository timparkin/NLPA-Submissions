from django.utils.safestring import mark_safe
import hashlib
import urllib
from django import template
from django.template.defaultfilters import stringfilter
from libgravatar import Gravatar

register = template.Library()

@register.filter
@stringfilter
def limit_length_tooltip(value):
    if len(value)>40:
        limitvalue = "%s...%s"%(value[:20], value[-20:])
        return mark_safe('<span data-bs-toggle="tooltip" data-bs-placement="top" title="%s">%s</span>'%(value,limitvalue))

    else:
        return value

import hashlib
import urllib
from django.utils.safestring import mark_safe


# return an image tag with the gravatar
# TEMPLATE USE:  {{ email|gravatar:150 }}
@register.filter
def gravatar(email, size=40):
    url = Gravatar(email)
    return mark_safe('<img class="rounded-circle" src="%s" height="%d" width="%d">' % (url.get_image(), size, size))
