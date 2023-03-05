from django import template
from django.utils.html import strip_spaces_between_tags, strip_tags
from django.utils.text import Truncator
import readtime 

register = template.Library()


#Template tag for html sanitize
@register.filter(name='html_trunc')
def excerpt_with_ptag_spacing(value, arg):

    try:
        limit = int(arg)
    except ValueError:
        return 'Invalid literal for int().'

    # remove spaces between tags
    value = strip_spaces_between_tags(value)

    # add space before each P end tag (</p>)
    value = value.replace("</"," </")
    value = value.replace("<br>"," ")

    # strip HTML tags
    value = strip_tags(value)
    value = value.replace("&nbsp;"," ")
    value = value.replace("&quot;"," ")

    # other usage: return Truncator(value).words(length, html=True, truncate=' see more')
    return Truncator(value).chars(limit,truncate="...")

#Need a split function in template
@register.filter(name="split")
def split_tag(value,arg):
    return value.split(arg)

@register.filter(name='readtime')
def read_time(content):
    return readtime.of_html(content,wpm=265).text