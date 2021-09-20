from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='author')
        cls.user2 = User.objects.create_user(username='notauthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user1,
            text='Длина сообщения более 15 символов',
            pk=0,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client1 = Client()
        self.authorized_client2 = Client()
        self.authorized_client1.force_login(StaticURLTests.user1)
        self.authorized_client2.force_login(StaticURLTests.user2)

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_task_post_edit_url_redirect_nonauthor_on_post_details(self):
        """Страница по адресу /posts/<post_id>/edit перенаправит неавтора
         на страницу поста.
        """
        response = self.authorized_client2.get('/posts/0/edit/', follow=True)
        self.assertRedirects(
            response, '/posts/0/'
        )

    def test_task_create_url_redirect_unauthorized_on_post_details(self):
        """Страница по адресу /posts/<post_id>/edit перенаправит неавтора
         на страницу поста.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/signup/'
        )

    def test_urls_uses_correct_template_authorized(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': '/profile/author/',
            'posts/post_detail.html': '/posts/0/',
            'posts/create_post.html': '/create/',
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client1.get(adress)
                self.assertTemplateUsed(response, template)

    def test_task_detail_url_exists_at_desired_location_authorized(self):
        """Страница unexisting_page/ вернет 404 как авторизованному, так и
        неавторизованному пользоватетелю"""
        response = self.guest_client.get('unexisting_page/')
        self.assertEqual(response.status_code, 404)
        response = self.authorized_client1.get('unexisting_page/')
        self.assertEqual(response.status_code, 404)
