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
            text='Длина сообщения более 15 символов',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__"""
        post = PostModelTest.post
        post_object_name = str(post)
        self.assertEqual(post_object_name, 'Длина сообщения')
        group = PostModelTest.group
        group_object_name = str(group)
        self.assertEqual(group_object_name, 'Тестовая группа')
