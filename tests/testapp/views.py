from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from tests.testapp.models import User
from tests.testapp.serializers import UserSerializer

from drf_guard.operators import And, Or, Not
from .permissions import IsAdminUser, IsSelfUser, IsTeacherAccessingStudent
from drf_guard.permissions import HasRequiredGroups, HasRequiredPermissions


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint that allows users to be viewed or edited."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (HasRequiredGroups, HasRequiredPermissions)
    http_method_names = ['get', 'put', 'patch', 'delete']
    access_rules = {
        'GET': {
            'list': {
                'groups': ['admin'],
                'permissions': [IsAuthenticated]
            },
            'retrieve': {
                'groups': '__any__',
                'permissions': [
                    IsAuthenticated, And,
                    [IsSelfUser, Or, IsAdminUser, Or, IsTeacherAccessingStudent]
                ]
            },
        },
        'PUT': {
            'groups': '__any__',
            'permissions': [IsAuthenticated, [IsSelfUser, Or, IsAdminUser]]
        },
        'PATCH': {
            'groups': '__any__',
            'permissions': [IsAuthenticated, [IsSelfUser, Or, IsAdminUser]]
        },
        'DELETE': {
            'groups': [Not, 'student'],
            'permissions': [IsAuthenticated]
        }
    }
