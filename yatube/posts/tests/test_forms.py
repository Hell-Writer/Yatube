import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_auth = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test_slug2',
            description='Тестовое описание2',
        )
        cls.post = Post.objects.create(
            text='Тест',
            author=cls.user_auth,
            group=Group.objects.get(slug='test_slug'),
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_author = Client()
        self.user_author.force_login(self.user_auth)

    def test_create_post_form(self):
        """Тестируем создание поста"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст для формы',
            'group': self.group.id
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(text='Тестовый текст для формы').exists()
        )
        self.assertEqual(
            Post.objects.get(text='Тестовый текст для формы').author,
            self.user
        )
        self.assertEqual(
            Post.objects.get(text='Тестовый текст для формы').group,
            self.group
        )

    def test_edit_post_form(self):
        """Тестируем редактирование поста"""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Изменённый Тестовый текст для формы',
            'group': self.group2.id,
            'image': uploaded
        }
        self.user_author.post(
            reverse('posts:post_edit', kwargs={'post_id': 1}),
            data=form_data
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Изменённый Тестовый текст для формы',
                image='posts/small.gif'
            ).exists()
        )
        response = self.user_author.get(
            reverse('posts:group_list',
                    kwargs={'slug': 'test_slug'}
                    )
        )
        self.assertEqual(
            list(response.context.get('page_obj').object_list),
            []
        )

    def test_form_post_image(self):
        """
        Проверяем правильно ли работает сохранение
        и отображение картинки нового поста
        """
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small2.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст для рисунка',
            'group': self.group2.id,
            'image': uploaded
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст для рисунка',
                image='posts/small2.gif'
            ).exists()
        )
        self.assertIsNotNone((Post.objects.get(
            text='Тестовый текст для рисунка'
        ).image))

    def test_comment_form(self):
        """Тестируем добавление комментариев"""
        form_data = {
            'text': 'Тестовый коммент'
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': 1}),
            data=form_data
        )
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый коммент'
            ).exists()
        )
