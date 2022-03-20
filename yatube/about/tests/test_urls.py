# about/tests/test_urls.py
from http import HTTPStatus

from django.test import Client, TestCase

# Импорты отсортированы библиотекой isort

ABOUT_AUTHOR = '/about/author/'
ABOUT_TECH = '/about/tech/'


class AboutURLTests(TestCase):
    '''Тест доступности статических страниц'''
    def setUp(self):
        self.guest_client = Client()

    def test_static_urls_availability(self):
        '''Страницы ABOUT_AUTHOR и ABOUT_TECH доступны
        для не авторизованного пользователя.
        '''
        adresses = (ABOUT_AUTHOR, ABOUT_TECH)
        for adress in adresses:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)
