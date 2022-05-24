from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Post_writer')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
         )

        cls.authorised_client = Client()
        cls.authorised_client.force_login(cls.user)

    def test_form_create(self):
        '''Проверяем, что форма create_post создает запись в БД'''
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовая запись',
            'group': self.group.id
        }
        # Отправляем POST-запрос
        self.authorised_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        # Проверяем, что увеличилось число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_form_post_edit(self):
        '''Проверяем, что форма post_edit редактирует запись в БД'''
        post_for_edit = Post.objects.create(
            author=PostFormTest.user,
            text='Тестовый пост 2',
        )
        id_post = post_for_edit.id
        form_data = {
            'text': 'New',
            'group': self.group.id
        }
        # POST-запрос на редактирование формы
        self.authorised_client.post(
            reverse('posts:post_edit', kwargs={'post_id': id_post}),
            data=form_data,
        )
        post_for_edit = Post.objects.get(pk=id_post)
        self.assertEqual(post_for_edit.text, form_data['text'])
        self.assertEqual(post_for_edit.group.id, form_data['group'])
