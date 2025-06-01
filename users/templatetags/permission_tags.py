from django import template
from users.utils import user_has_permission

register = template.Library()

@register.filter
def has_permission(user, permission_name):
    """
    Template filter to check if user has specific permission
    
    Usage in template:
    {% if user|has_permission:"create_company" %}
        <a href="...">إنشاء شركة</a>
    {% endif %}
    """
    return user_has_permission(user, permission_name)

@register.simple_tag
def user_can(user, permission_name):
    """
    Template tag to check if user has specific permission
    
    Usage in template:
    {% user_can user "create_company" as can_create_company %}
    {% if can_create_company %}
        <a href="...">إنشاء شركة</a>
    {% endif %}
    """
    return user_has_permission(user, permission_name)

@register.inclusion_tag('users/permission_check.html')
def show_if_permitted(user, permission_name, content=""):
    """
    Inclusion tag to show content only if user has permission
    
    Usage in template:
    {% show_if_permitted user "create_company" %}
        <a href="...">إنشاء شركة</a>
    {% endshow_if_permitted %}
    """
    return {
        'has_permission': user_has_permission(user, permission_name),
        'content': content
    }
