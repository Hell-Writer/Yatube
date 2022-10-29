from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для тестовых тестов',
        )

    def test_model_Group_has_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(str(self.group), self.group.title)

    def test_model_Post_has_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(str(self.post), self.post.text[:15])

    def test_model_Post_has_correct_verbose(self):
        """Проверка содержания verbose_name"""
        field_verboses = {
            'author': 'Автор',
            'pub_date': 'Время публикации',
            'text': 'Текст поста',
            'image': 'Картинка',
            'group': 'Группа'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).verbose_name, expected)

    def test_model_Post_has_correct_help_text(self):
        """Проверка содержания help_text"""
        field_helps = {
            'text': 'Введите текст поста',
            'image': 'Прикрепите картинку',
            'group': 'Выберите группу'
        }
        for value, expected in field_helps.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).help_text, expected)
