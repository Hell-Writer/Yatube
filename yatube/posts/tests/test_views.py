import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, Follow

User = get_user_model()
VIEWABLE_POSTS = settings.VIEWABLE_POSTS
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_auth = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        posts = [
            Post(text=f'Тестовый пост {i}',
                 author=cls.user_auth,
                 group=Group.objects.get(slug='test_slug')) for i in range(13)
        ]
        Post.objects.bulk_create(posts)
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test_slug_2',
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            text='Новый Тест',
            author=cls.user_auth,
            group=Group.objects.get(slug='test_slug_2')
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

    def test_namespace(self):
        """Проверяем правильно ли работают namespace"""
        templates_url_names = (
            ('posts/index.html', reverse('posts:index')),
            ('posts/create_post.html', reverse('posts:post_create')),
            ('posts/create_post.html', reverse('posts:post_edit', kwargs={
                'post_id': 1
            })),
            ('posts/profile.html', reverse('posts:profile', kwargs={
                'username': 'auth'
            })),
            ('posts/post_detail.html', reverse('posts:post_detail', kwargs={
                'post_id': 1
            })),
            ('posts/group_list.html', reverse('posts:group_list', kwargs={
                'slug': 'test_slug'
            }))
        )
        for template, name in templates_url_names:
            with self.subTest(name=name):
                response = self.user_author.get(name)
                self.assertTemplateUsed(response, template)

    def test_post_detail(self):
        """Проверяем правильно ли работает страница одного поста"""
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': 1}
        ))
        self.assertEqual(
            response.context.get('post').text,
            Post.objects.get(pk=1).text
        )

    def test_group_list(self):
        """Проверяем правильно ли работает страница группы"""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'test_slug'}
        ))
        self.assertEqual(
            response.context.get('page_obj').object_list,
            list(Post.objects.filter(group=self.group))[:VIEWABLE_POSTS]
        )
        self.assertEqual(len(response.context.get('page_obj').object_list), 10)
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context.get('page_obj').object_list), 4)

    def test_index(self):
        """Проверяем правильно ли работает главная страница"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            list(response.context.get('page_obj').object_list),
            list(Post.objects.all()[:VIEWABLE_POSTS])
        )
        self.assertEqual(len(response.context.get('page_obj').object_list), 10)
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context.get('page_obj').object_list), 4)

    def test_profile(self):
        """Проверяем правильно ли работает страница профиля"""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': 'auth'}
        ))
        self.assertEqual(
            response.context.get('page_obj').object_list,
            list(Post.objects.filter(
                author=User.objects.get(username='auth')
            ))[:VIEWABLE_POSTS]
        )
        self.assertEqual(len(response.context.get('page_obj').object_list), 10)
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context.get('page_obj').object_list), 4)

    def test_post_create(self):
        """Проверяем правильно ли работает страница создания поста"""
        response = self.authorized_client.get(reverse(
            'posts:post_create'
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit(self):
        """Проверяем правильно ли работает страница редактирования поста"""
        response = self.user_author.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': 1}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_created_post_group(self):
        """
        Проверяем правильно ли работает сохранение
        и отображение нового поста
        """
        form_data = {
            'text': 'Тестовый текст для формы',
            'group': self.group2.id
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        response_index = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            response_index.context.get('page_obj').object_list[0].group,
            self.group2
        )
        response_group = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test_slug_2'}
            )
        )
        self.assertEqual(
            response_group.context.get('page_obj').object_list[0].group,
            self.group2
        )
        response_profile = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': 'HasNoName'}
            )
        )
        self.assertEqual(
            response_profile.context.get('page_obj').object_list[0].group,
            self.group2
        )

    def test_created_post_image(self):
        """
        Проверяем правильно ли работает
        отображение картинки нового поста
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
            name='small.gif',
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
        response_index = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            response_index.context.get('page_obj').object_list[0].image.name,
            'posts/' + uploaded.name
        )
        response_profile = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'HasNoName'}))
        self.assertEqual(
            response_profile.context.get('page_obj').object_list[0].image.name,
            'posts/' + uploaded.name
        )
        response_group = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug_2'}))
        self.assertEqual(
            response_group.context.get('page_obj').object_list[0].image.name,
            'posts/' + uploaded.name
        )
        response_post = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={
                'post_id': Post.objects.get(
                    text='Тестовый текст для рисунка').pk}))
        self.assertEqual(
            response_post.context.get('post').image,
            'posts/' + uploaded.name
        )

    def test_cache(self):
        """
        Тестируем кэш
        """
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.context.get('page_obj').object_list
        Post.objects.get(pk=1).delete()
        response_old = self.authorized_client.get(reverse('posts:index'))
        old_posts = response_old.context.get('page_obj').object_list
        self.assertEqual(list(old_posts), list(posts))
        cache.clear()
        response_new = self.authorized_client.get(reverse('posts:index'))
        new_posts = response_new.context.get('page_obj').object_list
        self.assertEqual(list(old_posts), list(new_posts))

    def test_following(self):
        """
        Тестируем подписки
        """
        self.authorized_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': 'auth'}
            ),
            data={'username': 'auth'}
        )
        self.assertTrue(
            Follow.objects.filter(
                author=self.user_auth,
                user=self.user
            ).exists()
        )
        response_user = self.authorized_client.get(
            reverse(
                'posts:follow_index'
            )
        )
        response_author = self.user_author.get(
            reverse(
                'posts:follow_index'
            )
        )
        self.assertEqual(
            response_user.context.get('page_obj').object_list[0].text,
            'Новый Тест'
        )
        self.assertEqual(
            list(response_author.context.get('page_obj').object_list),
            []
        )
        Post.objects.create(
            text='Пост для теста отображения',
            author=self.user_auth,
            group=Group.objects.get(slug='test_slug_2')
        )
        response_user = self.authorized_client.get(
            reverse(
                'posts:follow_index'
            )
        )
        response_author = self.user_author.get(
            reverse(
                'posts:follow_index'
            )
        )
        self.assertEqual(
            response_user.context.get('page_obj').object_list[0].text,
            'Пост для теста отображения'
        )
        self.assertEqual(
            list(response_author.context.get('page_obj').object_list),
            []
        )
        self.authorized_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': 'auth'}
            ),
            data={'username': 'auth'}
        )
        response_user = self.authorized_client.get(
            reverse(
                'posts:follow_index'
            )
        )
        self.assertFalse(
            Follow.objects.filter(
                author=self.user_auth,
                user=self.user
            ).exists()
        )
        self.assertEqual(
            list(response_user.context.get('page_obj').object_list),
            []
        )
