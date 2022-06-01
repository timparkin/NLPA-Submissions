from django.utils.safestring import mark_safe
import hashlib
import urllib
from django import template
from django.template.defaultfilters import stringfilter
from libgravatar import Gravatar
import json
from libthumbor import CryptoURL

crypto = CryptoURL(key='holysmokesbatman')

register = template.Library()

@register.filter
@stringfilter
def limit_length_tooltip(value):
    if '/' in value:
        value = ''.join(value.split('/')[1:])
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
def isare(value):
    """ is or are """
    if value == 1:
        return '%s is'%value
    else:
        return '%s are'%value


@register.filter
def is_big_enough(value):
    """check for 4000px is OK, 3000px is maybe and add icons"""
    if 'x' in value:
        wtext,htext = value.split(' x ')
        w = int(wtext)
        h = int(htext)
        if w>4000 or h>4000:
            return mark_safe('<span data-bs-toggle="tooltip" data-bs-placement="top" title="Image must not be greater than 4000px on the long side"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#EE0000" class="bi bi-x-circle-fill" viewBox="0 0 16 16">  <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/></svg></span>')
        elif w==4000 or h==4000:
            return mark_safe('<span data-bs-toggle="tooltip" data-bs-placement="top" title="image size OK"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#008800" class="bi bi-check-circle-fill" viewBox="0 0 16 16">  <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/></svg></span>')
        elif w>=3000 or h>=3000:
            return mark_safe('<span data-bs-toggle="tooltip" data-bs-placement="top" title="3000px or greater is OK but we recommemd 4000px on the long side"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#FF8800" class="bi bi-question-circle-fill" viewBox="0 0 16 16"><path d="M9.05.435c-.58-.58-1.52-.58-2.1 0L.436 6.95c-.58.58-.58 1.519 0 2.098l6.516 6.516c.58.58 1.519.58 2.098 0l6.516-6.516c.58-.58.58-1.519 0-2.098L9.05.435zM5.495 6.033a.237.237 0 0 1-.24-.247C5.35 4.091 6.737 3.5 8.005 3.5c1.396 0 2.672.73 2.672 2.24 0 1.08-.635 1.594-1.244 2.057-.737.559-1.01.768-1.01 1.486v.105a.25.25 0 0 1-.25.25h-.81a.25.25 0 0 1-.25-.246l-.004-.217c-.038-.927.495-1.498 1.168-1.987.59-.444.965-.736.965-1.371 0-.825-.628-1.168-1.314-1.168-.803 0-1.253.478-1.342 1.134-.018.137-.128.25-.266.25h-.825zm2.325 6.443c-.584 0-1.009-.394-1.009-.927 0-.552.425-.94 1.01-.94.609 0 1.028.388 1.028.94 0 .533-.42.927-1.029.927z"/></svg></span>')
        else:
            return mark_safe('<span data-bs-toggle="tooltip" data-bs-placement="top" title="Image must 3000px or greater on the long side. We recommended 4000px"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#AA0000" class="bi bi-x-circle-fill" viewBox="0 0 16 16">  <path d="M11.46.146A.5.5 0 0 0 11.107 0H4.893a.5.5 0 0 0-.353.146L.146 4.54A.5.5 0 0 0 0 4.893v6.214a.5.5 0 0 0 .146.353l4.394 4.394a.5.5 0 0 0 .353.146h6.214a.5.5 0 0 0 .353-.146l4.394-4.394a.5.5 0 0 0 .146-.353V4.893a.5.5 0 0 0-.146-.353L11.46.146zM8 4c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 4.995A.905.905 0 0 1 8 4zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/></svg></span>')

    else:
        return mark_safe('<span data-bs-toggle="tooltip" data-bs-placement="top" title="There is a problem with this image, please try again"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#EE0000" class="bi bi-x-circle-fill" viewBox="0 0 16 16">  <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/></svg></span>')


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def entry_count(value):
    """test"""
    output = []
    for entry in value:
        imgurl = 'https://r8a7z2p5.stackpathcdn.com/%s'%entry.photo
        encurl = crypto.generate(
                width=200,
                smart=True,
                image_url=imgurl
            )
        entry_text = "%s %s"%('<img src="http://submit.naturallandscapeawards.com:8000%s" width="200">'%encurl, entry.category)
        output.append(entry_text)

    return mark_safe('<br>'.join(output))
