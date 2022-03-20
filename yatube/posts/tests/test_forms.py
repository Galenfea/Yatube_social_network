# posts/tests/tests_form.py
from time import sleep

from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User


GROUP_1_SLUG = 'test-slug'
GROUP_1_TITLE = 'Первая тестовая группа'
GROUP_1_DESCRIPTION = 'Тестовое описание группы'

GROUP_2_SLUG = 'best-slug'
GROUP_2_TITLE = 'Тестовая группа 2'
GROUP_2_DESCRIPTION = 'Тестовое описание группы 2'

POST_TEXT = 'Классовый пост'
POST_TEXT_EDITED = 'Отредактированный тестовый текст'

POSTS_CREATE = '/create/'
POSTS_PROFILE_URL = '/profile/user_1/'

TEST_TEXT = 'Тестовывй текст'

USER_1_NAME = 'user_1'


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_1_NAME)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(PostFormTests.user)
        cls.group = Group.objects.create(
            title=GROUP_1_TITLE,
            slug=GROUP_1_SLUG,
            description=GROUP_1_DESCRIPTION,
        )
        cls.form = PostForm()
        # Пост для редактирования
        cls.post = Post.objects.create(author=cls.user,
                                       text=POST_TEXT,
                                       group_id=cls.group.id
                                       )
        cls.POSTS_EDIT_URL = reverse('posts:post_edit',
                                     kwargs={'post_id': cls.post.pk}
                                     )
        cls.POSTS_DETAIL_URL = reverse('posts:post_detail',
                                       kwargs={'post_id': cls.post.pk}
                                       )

    def test_post_create(self):
        """Валидная форма создает запись."""
        posts_count = Post.objects.count()
        form_data = {'text': TEST_TEXT,
                     'group': self.group.id
                     }
        # Задержка перед созданием нового поста, чтобы
        # не перепутались классовый пост и новый.
        sleep(0.0001)
        response = self.authorized_client.post(POSTS_CREATE,
                                               data=form_data, follow=False)
        self.assertRedirects(response, POSTS_PROFILE_URL)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Из-за сортировки в модели, новый пост имеет индекс 0 в QuerySet
        post = Post.objects.all()[0]
        self.assertEqual(
            post.group, Group.objects.get(title=GROUP_1_TITLE)
        )
        self.assertEqual(post.text, TEST_TEXT)
        self.assertEqual(post.author, User.objects.get(username=USER_1_NAME))

    def test_post_edit(self):
        """Валидная форма изменяет существующую запись."""
        # Создание второй группы, для проверки редактирования поля группы
        group_2 = Group.objects.create(
            title=GROUP_2_TITLE,
            slug=GROUP_2_SLUG,
            description=GROUP_2_DESCRIPTION,
        )
        posts_count = Post.objects.count()
        # Отредактированные данные
        form_data = {
            'group': group_2.id,
            'text': POST_TEXT_EDITED
        }
        response = self.authorized_client.post(
            self.POSTS_EDIT_URL,
            data=form_data,
            follow=True
        )
        response_get = (self.authorized_client.get(self.POSTS_DETAIL_URL))
        # Запрос отредактированных параметров из обновлённого сообщения

        edited_post = {'group': Group.objects.get(
            title=response_get.context['group_name']).id,
            'text': response_get.context['post'].text}

        self.assertRedirects(response, self.POSTS_DETAIL_URL)
        # Проверка на то, что не создано нового сообщения.
        self.assertEqual(Post.objects.count(), posts_count)
        # И отредактировано старое
        self.assertEqual(edited_post, form_data)


class CommentTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.POST_URL = '/posts/1/'
        cls.user = User.objects.create_user(username=USER_1_NAME)
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',

        )
        cls.POST_COMMENT = '/posts/1/comment/'

    def test_add_comment(self):
        '''Проверяет появление поста на странице, после отправки.'''
        response_auth = self.authorized_client.get(self.POST_URL)
        post_id = response_auth.context.get('post').pk
        comments_count_before = Post.objects.get(pk=post_id
                                                 ).comments.all().count()
        form_data = {'text': 'текст комментария',
                     'author': self.user,
                     'post': post_id
                     }
        self.authorized_client.post(self.POST_COMMENT, data=form_data,
                                    follow=False)
        response_guest = self.guest_client.get(self.POST_URL)
        post_id_2 = response_guest.context.get('post').pk
        comments_count_after = Post.objects.get(pk=post_id_2
                                                ).comments.all().count()
        self.assertEqual(comments_count_before + 1, comments_count_after)
