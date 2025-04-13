# Create this file at: templates/chatapp/templatetags/chat_extras.py

from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)