from ..models import Group, Post
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.shortcuts import get_object_or_404


User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='form_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='form_test_slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тест формы пост',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Передаем пост-запросом валидную форму нового поста,
        проверяем, как он там"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тест формы пост 2',
            'group': PostCreateFormTests.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username':
                                     Post.objects.latest('id').author}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(text='Тест формы пост 2',
                                group=PostCreateFormTests.group.id,
                                ).exists()
        )

    def test_edit_post(self):
        """Редактируем пост и проверяем, изменился ли он"""
        self.post = Post.objects.create(
            text='Текст до редактирования',
            author=self.user,
        )
        edited_form_data = {
            'text': 'Текст после редактирования',
            'author': self.user,
        }
        self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={
                        "post_id": self.post.id}),
            data=edited_form_data,
            follow=True
        )

        self.edited_post = get_object_or_404(Post.objects.filter(
            id=self.post.id))
        self.assertEqual(self.edited_post.text, 'Текст после редактирования')