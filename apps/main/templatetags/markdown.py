from django import template
from django.utils.safestring import mark_safe
import markdown as md

register = template.Library()


@register.filter()
def markdown(value):
    """Convert markdown to HTML."""
    if not value:
        return ''
    return mark_safe(md.markdown(value, extensions=['fenced_code', 'tables']))


@register.simple_tag
def markdown_content(content):
    """Convert markdown content to HTML and return safe string."""
    if not content:
        return ''
    return mark_safe(md.markdown(content, extensions=['fenced_code', 'tables']))
