from django.urls import reverse_lazy
from rest_framework.test import APITestCase
from django.contrib.auth.models import Group
from tests.testapp.models import User


class Tests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create(username='admin', password='adminuser')
        self.student = User.objects.create(username='student', password='studentuser')
        self.teacher = User.objects.create(username='teacher', password='teacheruser')

        self.admin_group = Group.objects.create(name='admin')
        self.student_group = Group.objects.create(name='student')
        self.teacher_group = Group.objects.create(name='teacher')

        self.admin.groups.add(self.admin_group.id)
        self.student.groups.add(self.student_group.id)
        self.teacher.groups.add(self.teacher_group.id)

    def tearDown(self):
        User.objects.all().delete()
        Group.objects.all().delete()

    def test_list_with_admin(self):
        url = reverse_lazy("user-list")
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_list_with_student(self):
        url = reverse_lazy("user-list")
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)

    def test_list_with_teacher(self):
        url = reverse_lazy("user-list")
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)

    def test_retrieve_admin_with_admin_ac(self):
        url = reverse_lazy("user-detail", args=[self.admin.id])
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_retrieve_student_with_student_ac(self):
        url = reverse_lazy("user-detail", args=[self.student.id])
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_retrieve_teacher_with_teacher_ac(self):
        url = reverse_lazy("user-detail", args=[self.teacher.id])
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_retrieve_teacher_with_student_ac(self):
        url = reverse_lazy("user-detail", args=[self.teacher.id])
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)

    def test_retrieve_student_with_teacher_ac(self):
        url = reverse_lazy("user-detail", args=[self.student.id])
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_delete_student_own_ac(self):
        url = reverse_lazy("user-detail", args=[self.student.id])
        self.client.force_authenticate(user=self.student)
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, 403)
