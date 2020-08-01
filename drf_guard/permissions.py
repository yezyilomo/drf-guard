from rest_framework import permissions
from django.contrib.auth.models import Group, Permission

from .operators import Operator, Reducer


class HasRequiredGroups(permissions.BasePermission):
    """
    Ensure user is in required groups.
    """
    @classmethod
    def is_in_group(cls, user, group):
        if isinstance(group, (str, Group)):
            return user.groups.filter(name=group).exists()
        if isinstance(group, (list, tuple)):
            return cls.is_in_required_groups(user, group)
        if issubclass(group, Operator):
            return group()

    @classmethod
    def is_in_required_groups(cls, user, groups):
        if groups == '__any__':
            return True
        if not groups:
            # If there are no groups to check
            return False

        reducer = Reducer()
        return reducer(
            (cls.is_in_group(user, group) for group in groups)
        )

    @staticmethod
    def get_groups(request, view):
        # Get a mapping of methods -> access rules
        access_rules = getattr(view, "access_rules", {})

        # Get access rules for this particular request method.
        http_method_access_rules = access_rules.get(request.method, {})

        default_groups = '__any__'

        if view.action in ['list', 'retrieve']:
            # Get required group related access rules for list action
            http_method_access_rules = http_method_access_rules.get(
                view.action, {'groups': default_groups}
            )

        return http_method_access_rules.get('groups', default_groups)

    def has_permission(self, request, view):
        if view.action == 'retrieve':
            # Separate retrive URL(This will be handled in has_object_permission)
            return True

        required_groups = self.get_groups(request, view)
        return self.is_in_required_groups(request.user, required_groups)

    def has_object_permission(self, request, view, obj):
        if view.action == 'list':
            # Separate list URL(This will be handled in has_permission)
            return True

        required_groups = self.get_groups(request, view)
        return self.is_in_required_groups(request.user, required_groups)


class HasRequiredPermissions(permissions.BasePermission):
    """
    Ensure user is has required permissions.
    """
    @classmethod
    def has_required_permission(cls, permission, request, view, obj=None):
        if isinstance(permission, str):
            return request.user.has_perm(permission)
        elif isinstance(permission, (list, tuple)):
            return cls.has_required_permissions(permission, request, view, obj)
        elif isinstance(permission, Permission):
            return request.user.has_perm(permission.codename)
        elif issubclass(permission, permissions.BasePermission):
            if obj is None:
                return permission().has_permission(request, view)
            else:
                return permission().has_object_permission(request, view, obj)
        elif issubclass(permission, Operator):
            # Encountered an operator
            return permission()
        else:
            data_type = type(permission).__name__
            raise TypeError("`%s` is an invalid permission type." % data_type)

    @classmethod
    def has_required_permissions(cls, permissions, *args):
        if permissions == '__any__':
            return True
        if not permissions:
            # If there are no permissions to check
            return False

        reducer = Reducer()
        return reducer((
            cls.has_required_permission(permission, *args)
            for permission in permissions
        ))

    @staticmethod
    def get_permissions(request, view):
        # Get a mapping of methods -> access rules
        access_rules = getattr(view, "access_rules", {})

        # Get access rules for this particular request method.
        http_method_access_rules = access_rules.get(request.method, {})

        default_permissions = '__any__'

        if view.action in ['list', 'retrieve']:
            # Get access rules for list/retrieve action
            http_method_access_rules = http_method_access_rules.get(
                view.action, {'permissions': default_permissions}
            )

        return http_method_access_rules.get('permissions', default_permissions)

    def has_permission(self, request, view):
        required_permissions = self.get_permissions(request, view)
        return self.has_required_permissions(required_permissions, request, view)

    def has_object_permission(self, request, view, obj):
        required_permissions = self.get_permissions(request, view)
        return self.has_required_permissions(required_permissions, request, view, obj)
