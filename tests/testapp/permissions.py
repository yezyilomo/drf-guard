from rest_framework import permissions


class IsAllowedUser(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to check if user is admin
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.is_admin


class IsTeacherAccessingStudent(permissions.BasePermission):
    """
    Custom permission to check if user is admin
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_teacher and obj.is_student