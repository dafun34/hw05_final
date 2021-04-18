import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.core.cache import caches

from posts.models import Post, Group, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'

        )
        cls.test_user = User.objects.create(
            username='tester',
            email='testmail@test.com',
            password='12345678'
        )
        cls.test_user_follow = User.objects.create(
            username='friend',
            email='followme@test.com',
            password='123456789'
        )
        cls.test_user_follow_2 = User.objects.create(
            username='Nikita',
            email='nikita@test.com',
            password='password'
        )
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            description='Описание',
            slug='test'
        )
        cls.test_group_2 = Group.objects.create(
            title='Тестовая группа 2',
            description='Описание 2',
            slug='test2'
        )

        cls.obj = (Post(text='Тестовый текст %s' % i,
                        author=cls.test_user,
                        group=cls.test_group,
                        ) for i in range(13))

        cls.test_posts = Post.objects.bulk_create(cls.obj)

        cls.test_post_image = Post.objects.create(
            text='Тест с картинкой',
            author=cls.test_user,
            group=cls.test_group,
            image=cls.uploaded
        )

        cls.templates_url_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/new.html': reverse('posts:new_post'),
            'posts/group.html': reverse('posts:group',
                                        kwargs={'slug': 'test'}),
            'misc/500.html': reverse('500'),
            'misc/404.html': '404/'
        }

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = self.test_user
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.my_cache = caches['default']

    def tearDown(self):
        self.my_cache.clear()

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_page_show_correct_context(self):
        """страница /new/ использует нужный контекст"""
        response = self.authorized_client.get(reverse('posts:new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_group_pages_correct_context(self):
        """страница группы использует нужный контекст"""
        response = self.authorized_client.get(reverse('posts:group',
                                                      kwargs={'slug': 'test'}))
        response_group = response.context['group']
        self.assertEqual(response_group.title, 'Тестовая группа')
        self.assertEqual(response_group.slug, 'test')
        self.assertEqual(response_group.description, 'Описание')

    def test_index_page_shows_correct_context(self):
        """Проверяет соответствие вывода поста с указаной
        группой на index"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page'][0]
        post_text_0 = first_object.text
        post_author0 = first_object.author.username
        post_group_title0 = first_object.group.title
        post_group_slug0 = first_object.group.slug
        post_image = first_object.image
        self.assertEqual(post_text_0, 'Тест с картинкой')
        self.assertEqual(post_author0, 'tester')
        self.assertEqual(post_group_title0, 'Тестовая группа')
        self.assertEqual(post_group_slug0, 'test')
        self.assertEqual(post_image, 'posts/small.gif')

    def test_group_page_show_correct_context(self):
        """проверяет соответствие вывода поста
        с указаной группой в group"""
        response = self.authorized_client.get(reverse('posts:group',
                                                      kwargs={'slug': 'test'}))
        posts = response.context['page'][0]
        group = response.context['group']
        group_title = group.title
        group_description = group.description
        post_text = posts.text
        post_author = posts.author.username
        group_slug = posts.group.slug
        post_image = posts.image
        self.assertEqual(group_title, 'Тестовая группа')
        self.assertEqual(group_description, 'Описание')
        self.assertEqual(post_text, 'Тест с картинкой')
        self.assertEqual(post_author, 'tester')
        self.assertEqual(group_slug, 'test')
        self.assertEqual(post_image, 'posts/small.gif')

    def test_group_page_2_show_correct_context(self):
        """проверяет отсутствие поста в группе 2"""
        response = self.authorized_client.get(reverse('posts:group',
                                                      kwargs={'slug': 'test2'})
                                              )
        posts = response.context['page']
        group = response.context['group']
        group_title = group.title
        group_description = group.description
        self.assertEqual(group_title, 'Тестовая группа 2')
        self.assertEqual(group_description, 'Описание 2')
        self.assertNotEqual(posts, 'Тестовый текст 13')

    def test_username_show_correct_context(self):
        """проверяет содержимое контекста на профиле пользователя"""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'tester'}))
        posts = response.context['page'][0]
        posts_image = posts.image
        author = response.context['author']
        self.assertEqual(posts.text, 'Тест с картинкой')
        self.assertEqual(author.username, 'tester')
        self.assertEqual(posts_image, 'posts/small.gif')

    def test_username_post_id_show_correct_context(self):
        """проверяет содержимое контекста на странице поста"""
        response = self.authorized_client.get(reverse(
            'posts:post', kwargs={'username': 'tester', 'post_id': '14'}))
        post = response.context['post']
        post_image = post.image
        author = response.context['author']
        self.assertEqual(post.text, 'Тест с картинкой')
        self.assertEqual(author.username, 'tester')
        self.assertEqual(post.id, 14)
        self.assertEqual(post_image, 'posts/small.gif')

    def test_username_post_id_edit_show_correct_context(self):
        """проверяет содержимое контекста на странице поста"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'username': 'tester', 'post_id': '13'}))
        form = response.context['form']
        here = response.context['here']
        form_text = form.initial['text']
        form_group = form.initial['group']
        self.assertEqual(form_text, 'Тестовый текст 12')
        self.assertEqual(form_group, 1)
        self.assertEqual(here, True)

    def test_first_page_have_ten_records(self):
        """ Проверяет что на 1й странице 10 постов"""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_have_4_records(self):
        """Проверяет что на 2й странице 4 записи"""
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 4)

    def test_group_paginator(self):
        """Проверяет что в тесовой группе 10 записей"""
        response = self.guest_client.get(reverse('posts:group',
                                                 kwargs={'slug': 'test'}))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_cache_index(self):
        """Проверяет что кеш работает на странице index"""
        response = self.authorized_client.get(reverse('posts:index'))
        posts_first_try = response.content
        Post.objects.create(text='еще один объект', author=self.test_user)
        response_after_new = self.authorized_client.get(reverse('posts:index'))
        posts_second_try = response_after_new.content
        self.assertEqual(posts_first_try, posts_second_try)
        caches['default'].clear()
        response_after_clear = self.authorized_client.get(reverse
                                                          ('posts:index'))
        posts_third_try = response_after_clear.content
        self.assertNotEqual(posts_first_try, posts_third_try)

    def test_authorized_user_can_follow_users(self):
        """Проверяет, что залогиненый пользователь может подписываться на
        дпугих пользователей"""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'friend'}))
        user = response.context['user']
        author = response.context['author']
        first_follow_count = Follow.objects.filter(user=user).count()
        Follow.objects.create(
            user=user,
            author=author)
        second_follow_count = Follow.objects.filter(user=user).count()
        self.assertNotEqual(first_follow_count, second_follow_count)

    def test_authorized_user_can_unfollow(self):
        """Проверяет, что залогиненый пользователь может отписываться от
          других пользователей """
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'friend'}))
        user = response.context['user']
        author = response.context['author']
        first_follow_count = Follow.objects.filter(user=user).count()
        follow_object = Follow.objects.create(
            user=user,
            author=author)
        second_follow_count = Follow.objects.filter(user=user).count()
        self.assertNotEqual(first_follow_count, second_follow_count)
        follow_object.delete()
        third_follow_count = Follow.objects.filter(user=user).count()
        self.assertEqual(first_follow_count, third_follow_count)

    def test_authorized_user_can_see_in_self_follow_posts_by_following(self):
        """Новая запись пользователя появляется в ленте тех, кто на него
        подписан """
        friend = self.test_user_follow
        response = self.authorized_client.get(reverse('posts:follow_index'))
        first_posts_count = response.context['page'].paginator.count
        user = response.context['user']
        Follow.objects.create(user=user, author=friend)
        Post.objects.create(author=friend, text='мой первый пост')
        caches['default'].clear()
        response_after = self.authorized_client.get(reverse(
            'posts:follow_index'))
        second_posts_count = response_after.context['page'].paginator.count
        self.assertNotEqual(first_posts_count, second_posts_count)

    def test_authorized_user_cant_see_posts_in_follow_index_by_unffolow(self):
        """Новая запись пользователя не появляется в ленте тех,
         кто на него не подписан"""
        not_friend = self.test_user_follow
        response = self.authorized_client.get(reverse('posts:follow_index'))
        first_posts_count = response.context['page'].paginator.count
        Post.objects.create(author=not_friend, text='мой тестовый пост')
        caches['default'].clear()
        response_after = self.authorized_client.get(reverse(
            'posts:follow_index'))
        second_posts_count = response_after.context['page'].paginator.count
        self.assertEqual(first_posts_count, second_posts_count)


    def test_guest_cant_comment(self):
        """Аноним не может добавлять комменты"""
        response = self.guest_client.get(reverse(
            'posts:add_comment', kwargs={'username': 'tester',
                                         'post_id': '14'}))
        self.assertEqual(response.status_code, 302)
