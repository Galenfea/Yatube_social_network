# about/tests/test_views.py
from django.test import Client, TestCase
from django.urls import reverse


ABOUT_AUTHOR_TMPLT = 'about/author.html'
ABOUT_TECH_TMPLT = 'about/tech.html'


class AboutViewsTests(TestCase):
    '''Тест верной работы views приложения about'''
    def setUp(self):
        self.guest_client = Client()

    def test_static_temlates(self):
        '''Страницы ABOUT_AUTHOR и ABOUT_TECH используют
        верные шаблоны.
        '''
        adresses = {'about:author': ABOUT_AUTHOR_TMPLT,
                    'about:tech': ABOUT_TECH_TMPLT
                    }
        for adress, template in adresses.items():
            with self.subTest(adress=adress):
                # Reverse(namespace: name) не заменяется константой,
                # так как проверяем работу view функций
                response = self.guest_client.get(reverse(adress))
                self.assertTemplateUsed(response, template)
