
from django import template

# Import your custom filter
from .likes_extras import has_liked

# Register your custom filter
register = template.Library()
register.filter('has_liked', has_liked)