from django.utils.safestring import mark_safe

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

style="""
<style>
/* Tooltip container */
.tooltipy {
  position: relative;
  border-bottom: 1px dotted black; /* If you want dots under the hoverable text */
}

/* Tooltip text */
.tooltipy .tooltiptexty {
  visibility: hidden;
  background-color: black;
  color: #fff;
  text-align: center;
  padding: 5px 0;
  border-radius: 6px;
  white-space: nowrap !important;


  /* Position the tooltip text - see examples below! */
  position: absolute;
  z-index: 100000;
}

/* Show the tooltip text when you mouse over the tooltip container */
.tooltipy:hover .tooltiptexty {
  visibility: visible;

}
</style>
"""

@register.filter
@stringfilter
def limit_length_tooltip(value):
    if len(value)>40:
        limitvalue = "%s...%s"%(value[:15], value[-15:])
        return mark_safe("%s<span class=\"tooltipy\">%s<span class=\"tooltiptexty\">%s</span></span>"%(style,limitvalue,value))

    else:
        return value
