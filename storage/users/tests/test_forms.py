from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse


class RegisterUserTestCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.registration_path = reverse("users:register")
        # User.objects.create_user('homer', 'homer@simpson.net', 'simpson')
        # self.client.login(username='homer', password='simpson')
        self.data = {
            'username': 'Homer',
            'email': 'homer@simpson.ru',
            'first_name': 'Homer',
            'last_name': 'Simpson',
            'password1': 'garbage98',
            'password2': 'garbage98',
            'permission_code': 'poseidon3798',
        }

    def test_form_registration_get(self):
        response = self.client.get(self.registration_path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_user_registration_OK(self):

        user_model = get_user_model()
        response = self.client.post(self.registration_path, self.data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('users:login'))
        self.assertTrue(user_model.objects.filter(username=self.data['username']).exists())

    def test_user_registration_COMMON_PASSWORD(self):
        self.data['password1'] = '12345678a'
        self.data['password2'] = '12345678a'
        response = self.client.post(self.registration_path, self.data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Введённый пароль слишком широко распространён.', html=True)


    def test_user_registration_password_error(self):
        self.data['password2'] = '1nghng'
        response = self.client.post(self.registration_path, self.data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Введенные пароли не совпадают.', html=True)

    def test_user_registration_password_error(self):
        self.data['password2'] = '1nghng'
        response = self.client.post(self.registration_path, self.data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Введенные пароли не совпадают.', html=True)

