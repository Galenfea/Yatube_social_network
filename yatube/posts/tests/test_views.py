# posts/tests/test_views.py
import shutil
import tempfile
from time import sleep

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post, User

GROUP_1_SLUG = 'test-slug'
GROUP_1_TITLE = 'Тестовая группа'
GROUP_1_DESCRIPTION = 'Тестовое описание группы'
GROUP_1_URL = '/group/test-slug/'

GROUP_2_SLUG = 'best-slug'
GROUP_2_TITLE = 'Тестовая группа 2'
GROUP_2_DESCRIPTION = 'Тестовое описание группы 2'

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
TEMP_CACHE_TIME = 10

LAST_POST_IND = 16
# NUM_DIF_POSTS it is NUMBER_OF_DIFFERENT_POSTS
NUM_DIF_POSTS = 3
NUM_THE_SAME_TYPE_POSTS = 13

POSTS_INDEX_TMP = 'posts/index.html'
POSTS_INDEX_URL = '/'

POSTS_CREATE_TMP = 'posts/create_post.html'
POSTS_CREATE_URL = '/create/'
POSTS_DETAIL_TMP = 'posts/post_detail.html'
POSTS_EDIT_TMP = POSTS_CREATE_TMP
POSTS_GROUP_TMP = 'posts/group_list.html'
POSTS_PROFILE_TMP = 'posts/profile.html'
POSTS_PROFILE_USER_1_URL = '/profile/user_1/'
POSTS_FOLLOW_USER_1_URL = '/profile/user_1//follow/'

USER_1_NAME = 'user_1'
USER_2_NAME = 'user_2'
USER_3_NAME = 'user_3'


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_1_NAME)
        cls.user2 = User.objects.create_user(username=USER_2_NAME)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title=GROUP_1_TITLE,
            slug=GROUP_1_SLUG,
            description=GROUP_1_DESCRIPTION,
        )
        cls.group2 = Group.objects.create(
            title=GROUP_2_TITLE,
            slug=GROUP_2_SLUG,
            description=GROUP_2_DESCRIPTION,
        )

        cls.posts = []
        # Создание 16-ти постов. Первые три сообщения с индексами 0, 1, 2
        # имеют группу cls.group2 и автора cls.user2.
        # Это будет использовано при проверке паджинатора, чтобы убедиться,
        # что в контексте объект паджинатора содержит отфильтрованные
        # по группе и автору сообщения.
        for i in range(LAST_POST_IND):
            if i <= NUM_DIF_POSTS - 1:
                real_author = cls.user2
                real_group = cls.group2
            else:
                real_author = cls.user
                real_group = cls.group
            cls.posts.append(Post.objects.create(
                author=real_author,
                text=(f'Тестовый текст номер {i}'),
                group_id=real_group.id)
            )
            # Помогает не запутаться при сортировке
            sleep(0.0001)

    def setUp(self):
        cache.clear()

    def test_correct_template_in_all_views(self):
        """View функция использует соответствующий шаблон."""
        # Здесь не используются константы url-ов вместо
        # reverse(namespace: name), так как проверяется
        # именно работа view функций
        templates = {
            reverse('posts:index'): POSTS_INDEX_TMP,
            reverse('posts:post_detail', kwargs={'post_id':
                                                 LAST_POST_IND}):
            POSTS_DETAIL_TMP,
            reverse('posts:profile', kwargs={'username': USER_1_NAME}):
            POSTS_PROFILE_TMP,
            reverse('posts:post_edit', kwargs={'post_id': LAST_POST_IND}):
            POSTS_EDIT_TMP,
            reverse('posts:post_create'): POSTS_CREATE_TMP,
            reverse('posts:group_list', kwargs={'slug': GROUP_1_SLUG}):
            POSTS_GROUP_TMP
        }
        for reverse_name, template in templates.items():
            with self.subTest(reverse_name=reverse_name, template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_paginator_and_post_exist_on_all_pages(self):
        '''Проверка корректной работы паджинатора для всех view функций
        и существования сообщения с группой на всех страницах проекта.
        '''
        username = self.user.username
        slug = self.group.slug
        pages = {reverse('posts:index'): settings.POSTS_PER_PAGE,
                 reverse('posts:group_list', kwargs={'slug': slug}):
                 settings.POSTS_PER_PAGE,
                 reverse('posts:profile', kwargs={'username': username}):
                 settings.POSTS_PER_PAGE,
                 reverse('posts:index') + '?page=2':
                 LAST_POST_IND - settings.POSTS_PER_PAGE,
                 reverse('posts:group_list',
                         kwargs={'slug': slug}) + '?page=2': NUM_DIF_POSTS,
                 reverse('posts:profile',
                         kwargs={'username': username}
                         ) + '?page=2': NUM_DIF_POSTS
                 }
        for page_adress, posts_count in pages.items():
            with self.subTest(page_adress=page_adress):
                response = self.client.get(page_adress)
                self.assertEqual(len(response.context['page_obj']),
                                 posts_count)
                # Проверка существования поста на разных страницах,
                # если указана группа.
                # Поля ['page_obj'][0] в контексте всех страниц соответствуют
                # полям self.posts[15] =>
                # сортировка сообщений происходит по убыванию даты публикации.
                if posts_count == settings.POSTS_PER_PAGE:
                    first_object = response.context['page_obj'][0]
                    self.assertEqual(self.user, first_object.author)
                    self.assertEqual(self.posts[LAST_POST_IND - 1].text,
                                     first_object.text)
                    self.assertEqual(self.group.id, first_object.group_id)
                    self.assertEqual(self.posts[LAST_POST_IND - 1].pk,
                                     first_object.pk)

    # Проверка контекста страницы index не нужна, так как в контексте
    # передается только паджинатор, а он уже проверен в функции
    # test_paginator_and_post_exist_on_all_pages

    def test_group_context(self):
        """Шаблон group_list сформирован с контекстом group
        (паджинатор проверяется функцией
        test_paginator_and_post_exist_on_all_pages, возврат ошибки 404,
        в случае неверного адреса, проверяется в test_urls.py)."""
        response = (self.authorized_client.get(reverse('posts:group_list',
                    kwargs={'slug': self.group.slug})))
        self.assertEqual(response.context.get('group').title,
                         self.group.title)
        self.assertEqual(response.context.get('group').description,
                         self.group.description)
        self.assertEqual(response.context.get('group').slug,
                         self.group.slug)

    def test_profile_context(self):
        """Шаблон profile сформирован с контекстом author и
        count_posts (паджинатор проверяется функцией
        test_paginator_and_post_exist_on_all_pages)."""
        response = (self.authorized_client.
                    get(reverse('posts:profile',
                                kwargs={'username': self.user.username})))
        self.assertEqual(response.context.get('author').username,
                         self.user.username)
        self.assertEqual(response.context.get('count_posts'),
                         NUM_THE_SAME_TYPE_POSTS
                         )

    def test_post_details_context(self):
        """Шаблон post_detail сформирован с контекстом post,
        author, group_name, count_posts."""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail',
                                kwargs={'post_id': LAST_POST_IND})))
        # В списке posts нумерация с 0, а pk сообщений начинается с 1.
        self.assertEqual(self.posts[LAST_POST_IND - 1],
                         response.context.get('post')
                         )
        self.assertEqual(self.user.username,
                         response.context.get('author').username
                         )
        self.assertEqual(self.group.title, response.context.get('group_name'))
        # У пользователя cls.user 13 сообщений и 3 у cls.user_2
        self.assertEqual(NUM_THE_SAME_TYPE_POSTS,
                         response.context.get('count_posts')
                         )

    def test_create_post_context(self):
        """Шаблон post_create сформирован с контекстом form."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_context(self):
        """Шаблон post_edit сформирован с контекстом form, post_id, is_edit."""
        # Единственный тест, где нам нужно залогинить другого пользователя,
        # поэтому не в фикстурах.
        authorized_user_2 = Client()
        authorized_user_2.force_login(self.user2)

        response = self.authorized_client.get(reverse('posts:post_edit',
                                                      kwargs={'post_id': 16}))
        response2 = authorized_user_2.get(reverse('posts:post_edit',
                                                  kwargs={'post_id': 16}))
        is_edit = {USER_1_NAME: response.context.get('is_edit'),
                   USER_2_NAME: response2.context
                   }
        # Выбор последнего сообщения в базе, имеющего pk = 16.
        post_id = self.posts[15].pk
        # Получение id сообщения из контекста для дальнейшего сравнения
        # с тем, что в базе
        real_post_id = response.context.get('post_id')
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(post_id, real_post_id)
        self.assertEqual(is_edit[USER_1_NAME], True)
        self.assertIsNone(is_edit[USER_2_NAME])

    def test_create_post_with_other_group(self):
        '''Тестирование отсутствия новосозданного поста в группе,
        которая для него не предназначена.'''
        # Единственный тест, где нам нужен пост без группы.
        post = Post.objects.create(author=self.user,
                                   text=('Тестовый текст поста без группы')
                                   )
        # Если бы новый пост оказался в одной из групп, в которой он
        # не должен оказаться, то он был бы первым постом
        # на странице группы (сортировка в модели по убыванию даты).
        # Если это не так, то он не в группе.
        group_slugs = (GROUP_1_SLUG, GROUP_2_SLUG)
        for group_slug in group_slugs:
            response = (self.authorized_client.get(reverse('posts:group_list',
                                                   kwargs={'slug': group_slug})
                                                   )
                        )
            # Первый пост на странице, выдаваемый паджинатором
            post_in_group_id = response.context['page_obj'][0].pk
            self.assertNotEqual(post_in_group_id, post.pk)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageInPostsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=USER_1_NAME)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title=GROUP_1_TITLE,
            slug=GROUP_1_SLUG,
            description=GROUP_1_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group_id=cls.group.id,
            image=cls.uploaded
        )
        cls.POST_ID = 1
        cls.POST_URL = '/posts/1/'

    def setUp(self):
        cache.clear()

    def test_image_in_context_of_paginator(self):
        """В контексте шаблонов функций с паджинатором передаётся картинка,
        если она есть.
        """
        adresses = (POSTS_INDEX_URL,
                    GROUP_1_URL,
                    POSTS_PROFILE_USER_1_URL
                    )
        for adress in adresses:
            with self.subTest(adress=adress):
                response = (self.guest_client.
                            get(adress)
                            )
                context_image = response.context.get(
                    'page_obj')[self.POST_ID - 1].image
                self.assertEqual(self.post.image, context_image)

    def test_image_in_post_detail_context(self):
        '''В контексте шаблона post_detail передаётся картинка, если она есть.
        '''
        response = self.guest_client.get(self.POST_URL)
        # Не помещено в сабтест из-за того, что 'post' не query set как другие
        context_image = response.context.get('post').image
        self.assertEqual(self.post.image, context_image)

    def test_image_in_db_when_PostForm_sent(self):
        '''Создаётся запись в в бд при отправке поста с картинкой
        через форму PostForm.
        '''
        authorized_client = Client()
        authorized_client.force_login(self.user)
        form_data = {'text': 'тестовый текст',
                     'group': self.group.id,
                     'image': self.uploaded
                     }
        sleep(0.0001)
        authorized_client.post(POSTS_CREATE_URL, data=form_data, follow=False)
        self.assertTrue(Post.objects.get(image=f'posts/{self.uploaded}'))

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)


# @override_settings(CACHE_TIME=TEMP_CACHE_TIME)
class CachTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.CACHE_TEST_TEXT = 'Cache test text'
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=USER_1_NAME)
        cls.post = Post.objects.create(
            author=cls.user,
            text=cls.CACHE_TEST_TEXT,
        )
        sleep(0.0001)

    def setUp(self):
        cache.clear()

    def test_index_cache(self):
        response = self.guest_client.get(POSTS_INDEX_URL)
        self.post.delete()
        sleep(settings.CACHE_TIME - 1)
        response_2 = self.guest_client.get(POSTS_INDEX_URL)
        self.assertEqual(response.content, response_2.content)
        sleep(settings.CACHE_TIME + 1)
        response_3 = self.guest_client.get(POSTS_INDEX_URL)
        self.assertNotEqual(response_2.content, response_3.content)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.TEST_TEXT = 'test text'
        cls.guest_client = Client()
        cls.author = User.objects.create_user(username=USER_1_NAME)
        cls.follower = User.objects.create_user(username=USER_2_NAME)
        cls.nonfollower = User.objects.create_user(username=USER_3_NAME)
        cls.authorized_author = Client()
        cls.authorized_follower = Client()
        cls.authorized_nonfollower = Client()
        cls.authorized_author.force_login(cls.author)
        cls.authorized_follower.force_login(cls.follower)
        cls.authorized_nonfollower.force_login(cls.nonfollower)
        sleep(0.0001)

    def test_auth_user_can_follow(self):
        '''Проверяет появление сведений о подписке в базе,
        после подписки.'''
        self.authorized_follower.post(reverse('posts:profile_follow',
                                      kwargs={'username': self.author})
                                      )
        follow_status = Follow.objects.filter(user=self.follower)
        self.assertTrue(follow_status)

    def test_auth_user_can_unfollow(self):
        '''Проверяет удаление сведений о подписке в базе, после отписки.'''
        self.authorized_follower.post(reverse('posts:profile_follow',
                                      kwargs={'username': self.author})
                                      )
        self.authorized_follower.post(reverse('posts:profile_unfollow',
                                      kwargs={'username': self.author})
                                      )
        follow_status = Follow.objects.filter(user=self.follower)
        self.assertFalse(follow_status)

    def test_appear_new_post_in_post_feed(self):
        '''Проверка появления нового сообщения в ленте подписчика
        и не появления в ленте тех, кто не подписан.'''
        self.authorized_follower.post(reverse('posts:profile_follow',
                                      kwargs={'username': self.author})
                                      )
        post = Post.objects.create(author=self.author,
                                   text=self.TEST_TEXT)
        follow_index = reverse('posts:follow_index')
        post_for_follower = (self.authorized_follower.get(follow_index).
                             context['page_obj'][0].pk)
        try:
            post_for_non_follower = (self.authorized_nonfollower.
                                     get(follow_index).context['page_obj'][0]
                                     )
        except IndexError:
            post_for_non_follower = None
        self.assertEqual(post_for_follower, post.pk)
        self.assertNotEqual(post_for_non_follower, post.pk)

    def test_auth_user_cant_follow_himself(self):
        '''Проверяет возможность подписки на самого себя.'''
        self.authorized_author.post(reverse('posts:profile_follow',
                                            kwargs={'username': self.author}
                                            )
                                    )
        follow_status = Follow.objects.filter(user=self.follower)
        self.assertFalse(follow_status)
