# core/tests/test_views.py
from django.test import Client, TestCase
from django.urls import reverse

CON = {
    'TEMPLATE_403_csrf': 'core/403csrf.html',
    'TEMPLATE_403': 'core/404.html',
    'TEMPLATE_404': 'core/404.html',
    'TEMPLATE_500': 'core/500.html',
}


class CorePagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_correct_template_in_all_views(self):
        """View функция использует соответствующий шаблон."""
        templates = {
            reverse('core:csrf_failure'): CON['TEMPLATE_403_csrf'],
            reverse('core:permission_denied'): CON['TEMPLATE_403'],
            reverse('core:page_not_found'): CON['TEMPLATE_404'],
            reverse('core:server_error'): CON['TEMPLATE_500'],
        }
        for reverse_name, template in templates.items():
            with self.subTest(reverse_name=reverse_name, template=template):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
