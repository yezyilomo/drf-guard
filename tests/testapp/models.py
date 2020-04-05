from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    full_name = models.CharField(max_length=256, blank=True)
    phone = models.CharField(max_length=256, blank=True, null=True)

    @property
    def is_admin(self):
        return super().is_staff or self.groups.filter(name='admin').exists()

    @property
    def is_student(self):
        return self.groups.filter(name='student').exists()

    @property
    def is_teacher(self):
        return self.groups.filter(name='teacher').exists()