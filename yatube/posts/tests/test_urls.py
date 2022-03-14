# posts/tests/test_urls.py
from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post, User

GROUP_1_SLUG_URL = '/group/test-slug/'
GROUP_1_SLUG = 'test-slug'
GROUP_1_TITLE = 'Тестовая группа'
GROUP_1_DESCRIPTION = 'Тестовое описание группы'
GROUP_2_SLUG = 'best-slug'

POSTS_INDEX = "/"
POSTS_INDEX_TMP = 'posts/index.html'

POSTS_CREATE = '/create/'
POSTS_CREATE_UNAUTH = '/auth/login/?next=/create/'

POSTS_CREATE_TMP = 'posts/create_post.html'
POSTS_DETAIL_TMP = 'posts/post_detail.html'
POSTS_EDIT_TMP = POSTS_CREATE_TMP
POSTS_GROUP_TMP = 'posts/group_list.html'
POSTS_PROFILE_TMP = 'posts/profile.html'
POSTS_PROFILE_URL = '/profile/user_1/'

UNEXISTING = '/unexisting/'
USER_1_NAME = 'user_1'
USER_2_NAME = 'user_2'


class StaticURLTests(TestCase):
    '''Тесты статических страниц'''
    def setUp(self):
        self.guest_client = Client()

    def test_home_url_availability(self):
        '''Домашняя страница доступна для не авторизованного пользователя.
        '''
        response = self.guest_client.get(POSTS_INDEX)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.POST_URL = '/posts/1/'
        cls.POSTS_EDIT = '/posts/1/edit/'
        cls.POSTS_EDIT_UNAUTH = '/auth/login/?next=/posts/1/edit/'
        cls.POSTS_COMMENT = '/posts/1/comment/'
        cls.POSTS_COMMENT_UNAUTH = '/auth/login/?next=/posts/1/comment/'

        cls.user = User.objects.create_user(username=USER_1_NAME)
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title=GROUP_1_TITLE,
            slug=GROUP_1_SLUG,
            description=GROUP_1_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group_id=cls.group.id
        )

    def setUp(self):
        cache.clear()

    def test_200_and_404_for_unauthorized_user(self):
        """Существующий URL-адрес доступен для не авторизованного пользователя,
        не существующий выдаёт ошибку 404.
        """
        adresses = {
            POSTS_INDEX: HTTPStatus.OK,
            GROUP_1_SLUG_URL: HTTPStatus.OK,
            self.POST_URL: HTTPStatus.OK,
            POSTS_PROFILE_URL: HTTPStatus.OK,
            UNEXISTING: HTTPStatus.NOT_FOUND,
        }
        for adress, code_respone in adresses.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, code_respone)

    def test_create_and_edit_for_authorized_user(self):
        """Существующий URL-адрес доступен для не авторизованного пользователя,
        не существующий выдаёт ошибку 404.
        """
        adresses = (POSTS_CREATE,
                    self.POSTS_EDIT
                    )
        for adress in adresses:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_and_edit_for_anonym(self):
        """Страницы недоступные для неавторизованных пользователей
        перенаправляют пользователя на страницу логина.
        """
        adresses = {
            POSTS_CREATE: POSTS_CREATE_UNAUTH,
            self.POSTS_EDIT:
            self.POSTS_EDIT_UNAUTH,
            # Добавлена проверка того, что анонимного пользователя редиректит
            # при попытке написать комментарий
            self.POSTS_COMMENT: self.POSTS_COMMENT_UNAUTH
        }
        for adress, redirect_page in adresses.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertRedirects(response, redirect_page)

    def test_edit_for_nonauthor(self):
        '''Страница /posts/post_id/edit/ недоступна не автору.'''
        user_2 = User.objects.create_user(username=USER_2_NAME)
        authorized_client_2 = Client()
        authorized_client_2.force_login(user_2)
        response = authorized_client_2.get(self.POSTS_EDIT)
        self.assertRedirects(response, self.POST_URL)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        adresses = {
            POSTS_INDEX: POSTS_INDEX_TMP,
            GROUP_1_SLUG_URL: POSTS_GROUP_TMP,
            POSTS_CREATE: POSTS_CREATE_TMP,
            self.POSTS_EDIT: POSTS_EDIT_TMP,
            self.POST_URL: POSTS_DETAIL_TMP,
            POSTS_PROFILE_URL: POSTS_PROFILE_TMP,
        }
        for adress, template in adresses.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
