# posts/tests/test_models.py
from xml.etree.ElementTree import Comment

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from ..models import Comment, Follow, Group, Post

User = get_user_model()

# CON - CONSTANTS
CON = {
    'GROUP_SLUG': 'test-slug',
    'GROUP_TITLE': 'Тестовая группа',
    'GROUP_DESCRIPTION': 'Тестовое описание группы',
    'POST_TEXT': 'Тестовый текст',
    'COMMENTARY_TEXT': 'Тестовый комментарий',
    'EXPECTED_COMMENTARY_TEXT': 'Тестовый коммен',
    'USER_1_NAME': 'user_1',
    'USER_2_NAME': 'user_2',
    'INTEGRITY_ERROR': 'IntegrityError',
}


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=CON['USER_1_NAME'])
        cls.group = Group.objects.create(
            title=CON['GROUP_TITLE'],
            slug=CON['GROUP_SLUG'],
            description=CON['GROUP_DESCRIPTION'],
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=CON['POST_TEXT'],
        )
        cls.comment = Comment.objects.create(
            text=CON['COMMENTARY_TEXT'],
            author=cls.user,
            post=cls.post,
        )

    def test_models_have_correct_object_names(self):
        """Проверяется, корректная работа __str__ моделей."""
        str_models = {str(PostModelTest.group): CON['GROUP_TITLE'],
                      str(PostModelTest.post): CON['POST_TEXT'],
                      str(PostModelTest.comment):
                      CON['EXPECTED_COMMENTARY_TEXT']
                      }
        for model, expected_value in str_models.items():
            with self.subTest(model=model):
                self.assertEqual(
                    model, expected_value)


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=CON['USER_1_NAME'])
        cls.user_f = User.objects.create_user(username=CON['USER_2_NAME'])
        cls.follow = Follow.objects.create(
            user=cls.user_f,
            author=cls.user,
        )

    def test_follow_model_have_correct_object_name(self):
        """Проверяется, корректная работа __str__ модели Follow."""
        exepcted_value = f'{self.user_f} => {self.user}'
        self.assertEqual(str(FollowModelTest.follow), exepcted_value)

    def test_double_follow_constraint(self):
        """Проверяется ограничение модели на дублирование подписки"""
        try:
            double_follow = Follow.objects.create(
                user=self.user_f,
                author=self.user,
            )
        except IntegrityError:
            double_follow = CON['INTEGRITY_ERROR']
        self.assertEqual(double_follow, CON['INTEGRITY_ERROR'])

    def test_self_follow_constraint(self):
        """Проверяется ограничение модели на самоподписку"""
        try:
            self_follow = Follow.objects.create(
                user=self.user_f,
                author=self.user,
            )
        except IntegrityError:
            self_follow = CON['INTEGRITY_ERROR']
        self.assertEqual(self_follow, CON['INTEGRITY_ERROR'])
