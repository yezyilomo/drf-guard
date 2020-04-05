from rest_framework import permissions
from django.contrib.auth.models import Group, Permission

from .operators import Operator, Reducer


class HasRequiredGroups(permissions.BasePermission):
    """
    Ensure user is in required groups.
    """
    @classmethod
    def is_in_group(cls, user, group):
        if group == '__all__':
            return True
        if isinstance(group, (str, Group)):
            return user.groups.filter(name=group).exists()
        if isinstance(group, (list, tuple)):
            return cls.is_in_required_groups(user, group)
        if issubclass(group, Operator):
            return group()

    @classmethod
    def is_in_required_groups(cls, user, groups):
        if groups is None:
            # Don't check the permissions
            return True
            
        reducer = Reducer()
        return reducer(
                (cls.is_in_group(user, group) for group in groups)
            )

    def has_permission(self, request, view):
        if view.action == 'retrieve':
            # Separate retrive URL(This will be handled in has_object_permission)
            return True

        # Get a mapping of methods -> required group.
        required_groups_mapping = getattr(view, "groups_and_permissions", {})

        # Determine the required groups for this particular request method.
        required_groups = required_groups_mapping.get(request.method, {})

        if view.action == 'list':
            # Get required groups for list action
            required_groups = required_groups.get('list', {'groups': None, 'permissions': None})
        
        required_groups = required_groups.get('groups', None)

        # Return True if the user has all the required groups or is staff.
        return self.is_in_required_groups(request.user, required_groups)

    def has_object_permission(self, request, view, obj):
        if view.action == 'list':
            # Separate list URL(This will be handled in has_permission)
            return True

        # Get a mapping of methods -> required group.
        required_groups_mapping = getattr(view, "groups_and_permissions", {})

        # Determine the required groups for this particular request method.
        required_groups = required_groups_mapping.get(request.method, {})

        if view.action == 'retrieve':
            # Get required groups for retrieve action
            required_groups = required_groups.get('retrieve', {'groups': None, 'permissions': None})

        required_groups = required_groups.get('groups', None)

        # Return True if the user has all the required groups or is staff.
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
            raise TypeError("`%s` is invalid permission type." % data_type)

    @classmethod
    def has_required_permissions(cls, permissions, *args):
        if permissions is None:
            # Don't check the permissions
            return True

        reducer = Reducer()
        return reducer((
            cls.has_required_permission(permission, *args)
            for permission in permissions
        ))
        
    @staticmethod
    def get_permissions(request, view):
        # Get a mapping of methods -> required group.
        required_permissions_mapping = getattr(view, "groups_and_permissions", {})

        # Determine the required groups for this particular request method.
        required_permissions = required_permissions_mapping.get(request.method, {})

        if view.action == 'retrieve':
            required_permissions = required_permissions.get('retrieve', {'groups': None, 'permissions': None})
        elif view.action == 'list':
            required_permissions = required_permissions.get('list', {'groups': None, 'permissions': None})

        return required_permissions.get('permissions', None)

    def has_permission(self, request, view):
        required_permissions = self.get_permissions(request, view)
        return self.has_required_permissions(required_permissions, request, view)

    def has_object_permission(self, request, view, obj):
        required_permissions = self.get_permissions(request, view)
        return self.has_required_permissions(required_permissions, request, view, obj)
