
from django import template
from django.template.defaultfilters import stringfilter
import json

register = template.Library()
@register.filter
@stringfilter
def jsonify(value):
    """
    Converts a Python object (usually a list or dict) to a JSON string.
    This filter expects a string representation of a Python object,
    then converts it to JSON. This is often used for objects that
    have been stringified (e.g., from a list of dicts) before being
    passed to the template, or if you need to pass raw Python objects.
    """
    try:
        # If value is already a Python object passed directly
        if not isinstance(value, str):
            return json.dumps(value)
        # If value is a string representation of a Python object
        return json.dumps(eval(value)) # eval is risky, be careful with trusted input only
    except Exception as e:
        return f"Error: {e}"

# Alternative and safer approach if you pass the Python object directly to template
@register.filter
def to_json(obj):
    """
    Converts a Python object to a JSON string.
    Recommended if you pass the Python list of dicts directly to the template.
    """
    return json.dumps(obj)