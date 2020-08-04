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


class HasRequiredAccessRules(permissions.BasePermission):
    """
    Ensure user is has required permissions and is in required groups.
    """
    @classmethod
    def get_operator_or_operand_value(cls, operator_or_operand, groups_and_perms):
        if isinstance(operator_or_operand, str):
            # It's an operand
            operand = operator_or_operand
            try:
                return groups_and_perms[operand]
            except KeyError:
                operands = ['`%s`' % op for op in groups_and_perms.keys()]
                allowed_operands = ', '.join(operands)
                msg = (
                    "`%s` is an invalid operand, allowed operands are %s."
                ) % (operand, allowed_operands)
                raise TypeError(msg)

        elif isinstance(operator_or_operand, (list, tuple)):
            # It's sub expr
            sub_expr = operator_or_operand
            return cls.eval_groups_and_perms_expr(sub_expr, groups_and_perms)

        elif issubclass(operator_or_operand, Operator):
            # Encountered an operator
            operator = operator_or_operand
            return operator()

        else:
            # Invalid operand
            data_type = type(operator_or_operand).__name__
            operands = ['`%s`' % op for op in groups_and_perms.keys()]
            allowed_operands = ', '.join(operands)
            msg = (
                "`%s` is an invalid operand, allowed operands are %s."
            ) % (data_type, allowed_operands)
            raise TypeError(msg)

    @classmethod
    def eval_groups_and_perms_expr(cls, groups_and_perms_expr, groups_and_perms):
        reducer = Reducer()
        return reducer((
            cls.get_operator_or_operand_value(operator_or_operand, groups_and_perms)
            for operator_or_operand in groups_and_perms_expr
        ))

    @staticmethod
    def get_groups_and_perms_expr(request, view):
        # Get a mapping of methods -> access rules
        access_rules = getattr(view, "access_rules", {})

        # Get access rules for this particular request method.
        http_method_access_rules = access_rules.get(request.method, {})

        default_groups_and_perms_expr = ['groups', 'permissions']

        if view.action in ['list', 'retrieve']:
            # Get access rules for list/retrieve action
            http_method_access_rules = http_method_access_rules.get(
                view.action,
                {'expression': default_groups_and_perms_expr}
            )

        return http_method_access_rules.get(
            'expression',
            default_groups_and_perms_expr
        )

    def has_permission(self, request, view):
        groups_and_perms = {
            'groups': HasRequiredGroups().has_permission(request, view),
            'permissions': HasRequiredPermissions().has_permission(request, view)
        }

        groups_and_perms_expr = self.get_groups_and_perms_expr(request, view)
        return self.eval_groups_and_perms_expr(groups_and_perms_expr, groups_and_perms)

    def has_object_permission(self, request, view, obj):
        groups_and_perms = {
            'groups': HasRequiredGroups().has_object_permission(request, view, obj),
            'permissions': HasRequiredPermissions().has_object_permission(request, view, obj)
        }

        groups_and_perms_expr = self.get_groups_and_perms_expr(request, view)
        return self.eval_groups_and_perms_expr(groups_and_perms_expr, groups_and_perms)
