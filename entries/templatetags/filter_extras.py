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


@register.filter
@stringfilter
def tooltip(value, message):
    if len(value)>40:
        return mark_safe('<span data-bs-toggle="tooltip" data-bs-placement="top" title="%s">%s</span>'%(message,value))

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

@register.filter
def s3toCDN(value):
    """changes s3 links to CDN links"""
    return value.replace('https://nlpa-website-bucket.s3.amazonaws.com', 'https://r8a7z2p5.stackpathcdn.com')

@register.filter
def is_big_enough(value):
    """changes s3 links to CDN links"""
    if int(value.split(' x ')[0])>2047 or int(value.split(' x ')[1])>2047:
        return mark_safe('<span data-bs-toggle="tooltip" data-bs-placement="top" title="image size OK"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#00AA00" class="bi bi-check-circle-fill" viewBox="0 0 16 16">  <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/></svg></span>')
    else:
        return mark_safe('<span data-bs-toggle="tooltip" data-bs-placement="top" title="image smaller than recommended"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#880000" class="bi bi-x-circle-fill" viewBox="0 0 16 16">  <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/></svg></span>')
