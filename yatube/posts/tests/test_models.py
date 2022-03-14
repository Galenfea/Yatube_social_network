# posts/tests/test_models.py
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()

GROUP_SLUG = 'test-slug'
GROUP_TITLE = 'Тестовая группа'
GROUP_DESCRIPTION = 'Тестовое описание группы'
POST_TEXT = 'Тестовый текст'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        str_models = {str(PostModelTest.group): GROUP_TITLE,
                      str(PostModelTest.post): POST_TEXT
                      }
        for model, expected_value in str_models.items():
            with self.subTest(model=model):
                self.assertEqual(
                    model, expected_value)
