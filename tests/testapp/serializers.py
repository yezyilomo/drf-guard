from rest_framework import serializers
from tests.testapp.models import User


ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('student', 'Student'),
    ('teacher', 'Teacher')
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username'
        )
