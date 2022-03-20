# posts/tests/test_urls.py
# from http import HTTPStatus

from django.test import Client, TestCase

from ...posts.models import Group, Post, User

app_name = 'users'

CON = {
    'LOGOUT_URL': '/logout/',
    'LOGOUT_TEMPLATE': 'users/logged_out.html',
    'LOGIN_URL': 'login/',
    'LOGIN_TEMPLATE': 'users/login.html',
    'SIGNUP_URL': 'signup/',
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
        """URL-адрес использует соответствующий шаблон."""
        adresses = {
            CON['LOGIN_URL']: CON['LOGIN_TEMPLATE'],
            CON['SIGNUP_URL']: CON['SIGNUP_TEMPLATE'],
        }
        for adress, template in adresses.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
        response_auth = self.authorized_client.get(CON['LOGOUT_URL'])
        self.assertTemplateUsed(response_auth, CON['LOGOUT_TEMPLATE'])
