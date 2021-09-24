from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post
from django import forms

User = get_user_model()


class ViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authoruser = User.objects.create_user(username='author')
        cls.notauthoruser = User.objects.create_user(username='notauthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.authoruser,
            group=cls.group,
            text='Длина сообщения более 15 символов',
        )
        cls.post_notauthor = Post.objects.create(
            author=cls.notauthoruser,
            text='Второй пост, длина более 15 символов',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(ViewsTest.authoruser)

    def check_posts_context(self, context, answer_post):
        """Проверяет возвращаемый контекст"""
        self.assertEqual(context['page_obj'][0].text, answer_post.text)
        self.assertEqual(context['page_obj'][0].author, answer_post.author)
        self.assertEqual(context['page_obj'][0].group, answer_post.group)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group',
                    kwargs={'slug':
                            ViewsTest.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username':
                            ViewsTest.authoruser.username}
                    ): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': ViewsTest.post.pk}
                    ): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': ViewsTest.post.pk}
                    ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
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
                                              kwargs={'post_id':
                                                      ViewsTest.post.pk}))
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
                                              kwargs={'slug':
                                                      ViewsTest.group.slug
                                                      })
                                              )
        self.check_posts_context(response.context, ViewsTest.post)

    def test_profile_show_correct_context(self):
        """Из вью profile передается правильное количество
        постов и правильное их содержание."""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': ViewsTest.notauthoruser.username}
                    ))
        self.check_posts_context(response.context, ViewsTest.post_notauthor)
