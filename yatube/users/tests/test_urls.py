# users/tests/test_urls.py
from django.test import Client, TestCase

from posts.models import User

app_name = 'users'

CON = {
    'LOGOUT_URL': '/auth/logout/',
    'LOGOUT_TEMPLATE': 'users/logged_out.html',
    'LOGIN_URL': '/auth/login/',
    'LOGIN_TEMPLATE': 'users/login.html',
    'SIGNUP_URL': '/auth/signup/',
    'SIGNUP_TEMPLATE': 'users/signup.html',
    'USER_1': 'user_1'
}


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=CON['USER_1'])
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_urls_uses_correct_template(self):
        """URL-адреса login и signup используют соответствующие шаблоны."""
        adresses = {
            CON['LOGIN_URL']: CON['LOGIN_TEMPLATE'],
            CON['SIGNUP_URL']: CON['SIGNUP_TEMPLATE'],
        }
        for adress, template in adresses.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_logout_correct_template(self):
        """URL-адрес logout использует соответствующий шаблон."""
        response_auth = self.authorized_client.get(CON['LOGOUT_URL'])
        self.assertTemplateUsed(response_auth, CON['LOGOUT_TEMPLATE'])
