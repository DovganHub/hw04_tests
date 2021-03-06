from ..models import Group, Post
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

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

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Передаем пост-запросом валидную форму нового поста,
        проверяем, как он там"""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тест формы пост 2',
            'group': PostCreateFormTests.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username':
                                     self.user}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        last_post = Post.objects.latest('id')
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.group.id, form_data['group'])
        self.assertEqual(last_post.image.name.split('/')[1].split('_')[0],
                         form_data['image'].name.split('.')[0])
        self.assertEqual(last_post.author,
                         PostCreateFormTests.user)

    def test_edit_post(self):
        """Редактируем пост и проверяем, изменился ли он"""
        post = Post.objects.create(
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
                        'post_id': post.id}),
            data=edited_form_data,
            follow=True
        )
        edited_post = Post.objects.get(id=post.id)
        self.assertEqual(edited_post.text, edited_form_data['text'])
