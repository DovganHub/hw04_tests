from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post
from django import forms

User = get_user_model()


class TaskPagesTests(TestCase):
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
            group=cls.group,
            text='Длина сообщения более 15 символов',
            pk=0,

        )
        cls.post2 = Post.objects.create(
            author=cls.user2,
            text='Второй пост, длина более 15 символов',
            pk=1,

        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(TaskPagesTests.user1)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group',
                                             kwargs={'slug': 'test-slug'}),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={'username': 'author'}),
            'posts/post_detail.html': (reverse('posts:post_detail',
                                       kwargs={'post_id': '0'})),
            reverse('posts:post_edit',
                    kwargs={'post_id': '0'}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_edit',
                                              kwargs={'post_id': '0'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_group_list_show_correct_context(self):
        """Из вью group_list передается правильное количество
        постов и правильное их содержание."""
        response = self.authorized_client.get(reverse('posts:group',
                                              kwargs={'slug': 'test-slug'}))
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['page_obj'][0].text,
                         'Длина сообщения более 15 символов')
        self.assertEqual(response.context['page_obj'][0].author,
                         TaskPagesTests.user1)

    def test_profile_show_correct_context(self):
        """Из вью profile передается правильное количество
        постов и правильное их содержание."""
        response = self.authorized_client.get(reverse('posts:profile',
                                              kwargs={'username': 'notauthor'
                                                      }))
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['page_obj'][0].text,
                         'Второй пост, длина более 15 символов')
        self.assertEqual(response.context['page_obj'][0].author,
                         TaskPagesTests.user2)

    def test_create_post_index(self):
        """При добавлении нового поста он появляется в response вью index"""
        posts_counter_before = len(self.authorized_client.get(
                                   reverse('posts:index')).context['page_obj'])
        Post.objects.create(author=TaskPagesTests.user2, text='Новый пост',
                            group=TaskPagesTests.group)
        posts_counter_after = len(self.authorized_client.get(
                                  reverse('posts:index')).context['page_obj'])
        self.assertEqual(posts_counter_after, posts_counter_before + 1)

    def test_create_post_group(self):
        """При добавлении нового поста он появляется в response вью group"""
        posts_counter_before = len(self.authorized_client.get(
                                   reverse('posts:group',
                                           kwargs={'slug': 'test-slug'}
                                           )).context['page_obj'])
        Post.objects.create(author=TaskPagesTests.user2, text='Новый пост',
                            group=TaskPagesTests.group)
        posts_counter_after = len(self.authorized_client.get(
                                  reverse('posts:group',
                                          kwargs={'slug': 'test-slug'}
                                          )).context['page_obj'])
        self.assertEqual(posts_counter_after, posts_counter_before + 1)

    def test_create_post_profile(self):
        """При добавлении нового поста он появляется в response вью profile"""
        posts_counter_before = len(self.authorized_client.get(
                                   reverse('posts:profile',
                                           kwargs={'username': 'notauthor'}
                                           )).context['page_obj'])
        Post.objects.create(author=TaskPagesTests.user2, text='Новый пост',
                            group=TaskPagesTests.group)
        posts_counter_after = len(self.authorized_client.get(
                                  reverse('posts:profile',
                                          kwargs={'username': 'notauthor'}
                                          )).context['page_obj'])
        self.assertEqual(posts_counter_after, posts_counter_before + 1)
