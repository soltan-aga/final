from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles):
    """
    Decorator to check if user has required role
    
    Args:
        allowed_roles: list of allowed roles or single role string
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'يجب تسجيل الدخول أولاً')
                return redirect('login')
            
            if not hasattr(request.user, 'profile'):
                messages.error(request, 'لا يوجد ملف شخصي لهذا المستخدم')
                return redirect('home')
            
            user_role = request.user.profile.role
            if user_role not in allowed_roles:
                messages.error(request, f'ليس لديك صلاحية للوصول إلى هذه الصفحة. الأدوار المطلوبة: {", ".join(allowed_roles)}')
                return redirect('home')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def admin_required(view_func):
    """Decorator to require admin role"""
    return role_required(['admin'])(view_func)

def admin_or_manager_required(view_func):
    """Decorator to require admin or manager role"""
    return role_required(['admin', 'manager'])(view_func)

def can_create(model_name):
    """
    Decorator to check if user can create specific model
    
    Args:
        model_name: name of the model (e.g., 'company', 'product', etc.)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'يجب تسجيل الدخول أولاً')
                return redirect('login')
            
            if not hasattr(request.user, 'profile'):
                messages.error(request, 'لا يوجد ملف شخصي لهذا المستخدم')
                return redirect('home')
            
            user_role = request.user.profile.role
            permission_name = f'create_{model_name}'
            
            # Define permissions for each role
            permissions = {
                'admin': {
                    'create_company': True,
                    'create_branch': True,
                    'create_store': True,
                    'create_safe': True,
                    'create_contact': True,
                    'create_product': True,
                    'create_invoice': True,
                    'create_transaction': True,
                    'create_user': True,
                },
                'manager': {
                    'create_company': False,
                    'create_branch': True,
                    'create_store': True,
                    'create_safe': True,
                    'create_contact': True,
                    'create_product': True,
                    'create_invoice': True,
                    'create_transaction': True,
                    'create_user': False,
                },
                'employee': {
                    'create_company': False,
                    'create_branch': False,
                    'create_store': False,
                    'create_safe': False,
                    'create_contact': True,
                    'create_product': False,
                    'create_invoice': True,
                    'create_transaction': True,
                    'create_user': False,
                },
                'viewer': {
                    'create_company': False,
                    'create_branch': False,
                    'create_store': False,
                    'create_safe': False,
                    'create_contact': False,
                    'create_product': False,
                    'create_invoice': False,
                    'create_transaction': False,
                    'create_user': False,
                }
            }
            
            role_permissions = permissions.get(user_role, {})
            has_permission = role_permissions.get(permission_name, False)
            
            if not has_permission:
                messages.error(request, f'ليس لديك صلاحية لإنشاء {model_name}')
                return redirect('home')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def can_edit(model_name):
    """
    Decorator to check if user can edit specific model
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'يجب تسجيل الدخول أولاً')
                return redirect('login')
            
            if not hasattr(request.user, 'profile'):
                messages.error(request, 'لا يوجد ملف شخصي لهذا المستخدم')
                return redirect('home')
            
            user_role = request.user.profile.role
            permission_name = f'edit_{model_name}'
            
            # Define permissions for each role
            permissions = {
                'admin': {
                    'edit_company': True,
                    'edit_branch': True,
                    'edit_store': True,
                    'edit_safe': True,
                    'edit_contact': True,
                    'edit_product': True,
                    'edit_invoice': True,
                    'edit_transaction': True,
                    'edit_user': True,
                },
                'manager': {
                    'edit_company': False,
                    'edit_branch': True,
                    'edit_store': True,
                    'edit_safe': True,
                    'edit_contact': True,
                    'edit_product': True,
                    'edit_invoice': True,
                    'edit_transaction': True,
                    'edit_user': False,
                },
                'employee': {
                    'edit_company': False,
                    'edit_branch': False,
                    'edit_store': False,
                    'edit_safe': False,
                    'edit_contact': True,
                    'edit_product': False,
                    'edit_invoice': False,
                    'edit_transaction': False,
                    'edit_user': False,
                },
                'viewer': {
                    'edit_company': False,
                    'edit_branch': False,
                    'edit_store': False,
                    'edit_safe': False,
                    'edit_contact': False,
                    'edit_product': False,
                    'edit_invoice': False,
                    'edit_transaction': False,
                    'edit_user': False,
                }
            }
            
            role_permissions = permissions.get(user_role, {})
            has_permission = role_permissions.get(permission_name, False)
            
            if not has_permission:
                messages.error(request, f'ليس لديك صلاحية لتعديل {model_name}')
                return redirect('home')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def can_delete(model_name):
    """
    Decorator to check if user can delete specific model
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'يجب تسجيل الدخول أولاً')
                return redirect('login')
            
            if not hasattr(request.user, 'profile'):
                messages.error(request, 'لا يوجد ملف شخصي لهذا المستخدم')
                return redirect('home')
            
            user_role = request.user.profile.role
            permission_name = f'delete_{model_name}'
            
            # Define permissions for each role
            permissions = {
                'admin': {
                    'delete_company': True,
                    'delete_branch': True,
                    'delete_store': True,
                    'delete_safe': True,
                    'delete_contact': True,
                    'delete_product': True,
                    'delete_invoice': True,
                    'delete_transaction': True,
                    'delete_user': True,
                },
                'manager': {
                    'delete_company': False,
                    'delete_branch': False,
                    'delete_store': False,
                    'delete_safe': False,
                    'delete_contact': False,
                    'delete_product': False,
                    'delete_invoice': False,
                    'delete_transaction': False,
                    'delete_user': False,
                },
                'employee': {
                    'delete_company': False,
                    'delete_branch': False,
                    'delete_store': False,
                    'delete_safe': False,
                    'delete_contact': False,
                    'delete_product': False,
                    'delete_invoice': False,
                    'delete_transaction': False,
                    'delete_user': False,
                },
                'viewer': {
                    'delete_company': False,
                    'delete_branch': False,
                    'delete_store': False,
                    'delete_safe': False,
                    'delete_contact': False,
                    'delete_product': False,
                    'delete_invoice': False,
                    'delete_transaction': False,
                    'delete_user': False,
                }
            }
            
            role_permissions = permissions.get(user_role, {})
            has_permission = role_permissions.get(permission_name, False)
            
            if not has_permission:
                messages.error(request, f'ليس لديك صلاحية لحذف {model_name}')
                return redirect('home')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
