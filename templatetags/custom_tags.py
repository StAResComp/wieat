from django import template

register = template.Library()

@register.filter(is_safe=True)
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()
