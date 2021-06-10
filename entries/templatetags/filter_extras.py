from django.utils.safestring import mark_safe
import hashlib
import urllib
from django import template
from django.template.defaultfilters import stringfilter
from libgravatar import Gravatar
import json


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
    return mark_safe('<img class="rounded-circle" src="%s" height="%d" width="%d">' % (url.get_image(default="mm"), size, size))

@register.filter
def s3toCDN(value):
    """changes s3 links to CDN links"""
    return value.replace('https://nlpa-website-bucket.s3.amazonaws.com', 'https://r8a7z2p5.stackpathcdn.com')

@register.filter
def decodestatus(value):
    """test"""
    return value.replace('payment_pending','paid_nc')


@register.filter
def decodepaymentplan(value):
    """test"""
    if value is not None:
        payment_plan = json.loads(value)
        return "entries: %(entries)s, projects: %(portfolios)s"%payment_plan
    return ''


@register.filter
def is_big_enough(value):
    """check for 2048px is OK, 1600px is maybe and add icons"""
    if 'x' in value:
        wtext,htext = value.split(' x ')
        w = int(wtext)
        h = int(htext)
        if w>2047 or h>2047:
            return mark_safe('<span data-bs-toggle="tooltip" data-bs-placement="top" title="image size OK"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#008800" class="bi bi-check-circle-fill" viewBox="0 0 16 16">  <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/></svg></span>')
        elif w>1600 or h>1600:
            return mark_safe('<span data-bs-toggle="tooltip" data-bs-placement="top" title="we recommemd at least 2048px on the long side"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#FF8800" class="bi bi-question-circle-fill" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.496 6.033h.825c.138 0 .248-.113.266-.25.09-.656.54-1.134 1.342-1.134.686 0 1.314.343 1.314 1.168 0 .635-.374.927-.965 1.371-.673.489-1.206 1.06-1.168 1.987l.003.217a.25.25 0 0 0 .25.246h.811a.25.25 0 0 0 .25-.25v-.105c0-.718.273-.927 1.01-1.486.609-.463 1.244-.977 1.244-2.056 0-1.511-1.276-2.241-2.673-2.241-1.267 0-2.655.59-2.75 2.286a.237.237 0 0 0 .241.247zm2.325 6.443c.61 0 1.029-.394 1.029-.927 0-.552-.42-.94-1.029-.94-.584 0-1.009.388-1.009.94 0 .533.425.927 1.01.927z"/></svg></span>')
        else:
            return mark_safe('<span data-bs-toggle="tooltip" data-bs-placement="top" title="Image must be greater than 1600px on the long side. We recommended 2048px"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#EE0000" class="bi bi-x-circle-fill" viewBox="0 0 16 16">  <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/></svg></span>')

    else:
        return mark_safe('<span data-bs-toggle="tooltip" data-bs-placement="top" title="There is a problem with this image, please try again"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#EE0000" class="bi bi-x-circle-fill" viewBox="0 0 16 16">  <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/></svg></span>')


@register.filter
def entry_count(value):
    """test"""
    output = []
    for entry in value:
        entry_text = "%s %s"%('<img src="https://r8a7z2p5.stackpathcdn.com/%s" width="30">'%entry.photo, entry.category)
        output.append(entry_text)

    return mark_safe('<br>'.join(output))
