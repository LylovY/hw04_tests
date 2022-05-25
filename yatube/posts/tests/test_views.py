from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Post_writer')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.posts = {}
        for i in range(13):
            name = 'post{}'.format(i)
            cls.posts[name] = Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group,
            )
        cls.authorised_client = Client()
        cls.authorised_client.force_login(cls.user)
        cls.guest_client = Client()

    def test_pages_uses_correct_template(self):
        '''URL - адрес использует соответствующий шаблон'''
        id_post = PostPagesTest.posts['post0'].id
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            (
                reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            ): 'posts/group_list.html',
            (
                reverse('posts:profile', kwargs={'username': 'Post_writer'})
            ): 'posts/profile.html',
            (
                reverse('posts:post_detail', kwargs={
                        'post_id': id_post})
            ): 'posts/post_detail.html',
            (
                reverse('posts:post_edit', kwargs={
                        'post_id': id_post})
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorised_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        '''Шаблон index сформирован с правильным контекстом(список постов)'''
        page = Post.objects.select_related('author', 'group').all()[:10]
        response = self.authorised_client.get(reverse('posts:index'))
        self.assertEqual(
            list(response.context.get('page_obj').object_list), list(page)
        )

    def test_page_show_correct_context_group(self):
        '''Шаблон group_list сформирован
        с правильным контекстом(список постов, отфильтрованных по группе)'''
        page = Post.objects.filter(group=self.group).all()[:10]
        response = self.authorised_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        self.assertEqual(list(response.context.get(
            'page_obj').object_list), list(page))

    def test_page_show_correct_context_author(self):
        '''Шаблон profile сформирован
        с правильным контекстом
        (список постов, отфильтрованных по пользователю)'''
        page = Post.objects.filter(author=self.user).all()[:10]
        response = self.authorised_client.get(
            reverse('posts:profile', kwargs={'username': 'Post_writer'}))
        self.assertEqual(list(response.context.get(
            'page_obj').object_list), list(page))

    def test_post_page_show_correct_context_post_detail(self):
        '''Шаблон post_detail сформирован
        с правильным контекстом
        (один пост, отфильтрованный по id)'''
        self.user2 = User.objects.create_user(username='Post_writer2')
        self.post14 = Post.objects.create(
            author=self.user2,
            text='Тестовый пост от Post_writer2',
        )
        response = self.authorised_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 14}))
        page_post = response.context['post'].text
        self.assertEqual(page_post, self.post14.text)

    def test_post_page_show_correct_context_post_edit(self):
        '''Шаблон post_detail сформирован
        с правильным контекстом
        (форма редактирования поста, отфильтрованного по id)'''
        response = self.authorised_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 10}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_page_show_correct_context_creaete_post(self):
        '''Шаблон post_create сформирован
        с правильным контекстом
        (форма создания поста)'''
        response = self.authorised_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        group_test = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug2',
            description='Тестовое описание',
        )
        post_test = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=group_test,
        )
        addresses = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug2'}),
            reverse('posts:profile', kwargs={'username': 'Post_writer'}),
        ]
        # проверяем, что пост появляется на:
        # главной странице
        # странице группы
        # профайле пользователя
        for address in addresses:
            response = self.authorised_client.get(address)
            last_object_id = response.context['page_obj'][0].id
            self.assertEqual(last_object_id, post_test.id)
        # проверяем, что пост не попал в другую группу
        response = self.authorised_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        last_object_id = response.context['page_obj'][0].id
        self.assertNotEqual(last_object_id, post_test.id)

    class PaginatorViewsTest(TestCase):
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
                text='Тестовая пост',
            )
            cls.posts = {}
            for i in range(13):
                name = 'post{}'.format(i)
                cls.posts[name] = Post.objects.create(
                    author=cls.user,
                    text='Тестовый пост'
                )
            cls.authorised_client = Client()
            cls.authorised_client.force_login(cls.user)
            cls.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        '''На первой странице отображается 10 постов'''
        addresses = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'Post_writer'}),
        ]
        for address in addresses:
            response = self.authorised_client.get(address)
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        '''На второй странице отображается 3 поста'''
        addresses = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'Post_writer'}),
        ]
        for address in addresses:
            response = self.authorised_client.get(address + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 3)
