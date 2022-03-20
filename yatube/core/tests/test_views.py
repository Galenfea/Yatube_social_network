# core/tests/test_views.py
from django.test import Client, TestCase

CON = {
    'TEMPLATE_404': 'core/404.html',
    'UNEXISTING': '/unexisting/',
}


class CorePagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_correct_template_in_all_views(self):
        """View функция использует соответствующий шаблон."""
        response = self.guest_client.get(CON['UNEXISTING'])
        self.assertTemplateUsed(response, CON['TEMPLATE_404'])
