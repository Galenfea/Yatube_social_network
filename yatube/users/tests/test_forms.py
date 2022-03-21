# users/tests/test_forms.py
from django.test import Client, TestCase

from posts.models import User

CON = {
    'FIRST_NAME': 'Jhon',
    'LAST_NAME': 'Snow',
    'USERNAME': 'King0fTheNorth',
    'EMAIL': 'bastard@winterfell.no',
    'USER_CREATE_URL': '/auth/signup/',
    'SUCCSESS_URL': '/',
    'PASSWORD': 'Marmelado4ka14',
}


class CreationFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_user_signup(self):
        """Валидная форма создает запись."""
        users_count = User.objects.count()
        form_data = {'first_name': CON['FIRST_NAME'],
                     'last_name': CON['LAST_NAME'],
                     'username': CON['USERNAME'],
                     'email': CON['EMAIL'],
                     'password1': CON['PASSWORD'],
                     'password2': CON['PASSWORD']
                     }
        response = self.guest_client.post(CON['USER_CREATE_URL'],
                                          data=form_data, follow=True)
        self.assertRedirects(response, CON['SUCCSESS_URL'])
        new_user = User.objects.all()[0]
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertEqual(new_user.first_name, CON['FIRST_NAME'])
        self.assertEqual(new_user.last_name, CON['LAST_NAME'])
        self.assertEqual(new_user.username, CON['USERNAME'])
        self.assertEqual(new_user.email, CON['EMAIL'])
