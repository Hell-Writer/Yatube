from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        """Тестируем главную страницу"""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class URLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_auth = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_auth,
            text='Тестовый пост для тестовых тестов',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_author = Client()
        self.user_author.force_login(self.user_auth)

    def test_pages_accesability(self):
        """Тестируем доступность страниц для разных категорий пользователей"""
        adress_auth_not_needed = [
            '/',
            '/group/test_slug/',
            '/profile/auth/',
            '/posts/1/'
        ]
        adress_auth_needed = [
            '/create/'
        ]
        adress_author_needed = [
            '/posts/1/edit/'
        ]
        for url in adress_auth_not_needed:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            response = self.authorized_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)
        for url in adress_auth_needed:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.FOUND)
            self.assertRedirects(
                response,
                reverse('users:login') + '?next=%2Fcreate%2F'
            )
            response = self.authorized_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)
        for url in adress_author_needed:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.FOUND)
            self.assertRedirects(
                response,
                reverse('users:login') + '?next=%2Fposts%2F1%2Fedit%2F'
            )
            response = self.authorized_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.FOUND)
            self.assertRedirects(
                response,
                reverse('posts:profile', kwargs={'username': 'HasNoName'})
            )
            response = self.user_author.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_special_pages_accesability(self):
        """
        Тестируем доступность особых страниц
        для разных категорий пользователей
        """
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response = self.guest_client.get('/posts/1/comment/')
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=%2Fposts%2F1%2Fcomment%2F'
        )
        response = self.authorized_client.get('/posts/1/comment/')
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': 1})
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = (
            ('posts/index.html', '/'),
            ('posts/create_post.html', '/create/'),
            ('posts/create_post.html', '/posts/1/edit/'),
            ('posts/profile.html', '/profile/HasNoName/'),
            ('posts/post_detail.html', '/posts/1/'),
            ('posts/group_list.html', '/group/test_slug/'),
            ('core/404.html', '/unexisting_page/')
        )
        for template, address in templates_url_names:
            with self.subTest(address=address):
                response = self.user_author.get(address)
                self.assertTemplateUsed(response, template)
