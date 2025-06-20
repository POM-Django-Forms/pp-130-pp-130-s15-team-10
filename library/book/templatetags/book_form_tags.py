from django import template

register = template.Library()

@register.filter
def attr(field, args):
    """Usage: {{ field|attr:'class=form-control' }}"""
    try:
        key, val = args.split('=')
        return field.as_widget(attrs={key: val})
    except:
        return field
