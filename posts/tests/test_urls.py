from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post, Group
from django.urls import reverse


User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_test = Group.objects.create(
            title='Тестовая группа',
            slug='test'
        )
        cls.user_test = User.objects.create_user(
            username='tester',
            email='testmail@test.com',
            password='12345678'
        )
        cls.user_test_2 = User.objects.create_user(
            username='tester_2',
            email='testmail_2@test.com',
            password='12345678'
        )
        cls.post_test = Post.objects.create(
            text='Тестовый текст',
            author=cls.user_test,
            group=cls.group_test
        )
        cls.templates_url_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/new.html': (
                reverse('posts:new_post'),
                reverse('posts:post_edit', kwargs={
                    'username': 'tester', 'post_id': '1'})),
            'posts/group.html': reverse('posts:group', kwargs={
                'slug': 'test'}),
            'posts/profile.html': reverse('posts:profile', kwargs={
                'username': 'tester'}),
            'posts/post.html': reverse('posts:post', kwargs={
                'username': 'tester', 'post_id': '1'}),
        }
        cls.authorized_urls = [
            reverse('posts:index'),
            reverse('posts:group', kwargs={'slug': 'test'}),
            reverse('posts:new_post'),
            reverse('posts:profile', kwargs={'username': 'tester'}),
            reverse('posts:post',
                    kwargs={'username': 'tester', 'post_id': '1'}),
            reverse('posts:post_edit',
                    kwargs={'username': 'tester', 'post_id': '1'})
        ]
        cls.urls_names = [
            reverse('posts:index'),
            reverse('posts:group', kwargs={'slug': 'test'}),
            reverse('posts:new_post')
        ]
        cls.guest_links = [
            reverse('posts:index'),
            reverse('posts:group', kwargs={'slug': 'test'}),
            reverse('posts:new_post'),
            reverse('posts:profile', kwargs={'username': 'tester'}),
            reverse('posts:post',
                    kwargs={'username': 'tester', 'post_id': '1'})
        ]
        cls.guest_redirect_links = [
            reverse('posts:new_post'),
            reverse('posts:post_edit',
                    kwargs={'username': 'tester', 'post_id': '1'})
        ]

    def setUp(self):
        # создаем неавторизованого пользователя
        self.guest_client = Client()
        # Создаем авторизованого автора пользователя
        self.authorized_client = Client()
        # Создаем авторизованого не автора
        self.authorized_client_not_author = Client()
        # Авторизуем пользователя автора
        self.authorized_client.force_login(self.user_test)

    def test_urls_authorized(self):
        """ авторизованный клиент может пройти по любой ссылке из списка"""
        for link in self.urls_names:
            with self.subTest():
                response = self.authorized_client.get(link)
                self.assertEqual(response.status_code, 200)

    def test_authorized_urls_authorized(self):
        """проверяет доступные ссылки для авторизованного пользователя"""
        for link in self.authorized_urls:
            with self.subTest():
                response = self.authorized_client.get(link)
                self.assertEqual(response.status_code, 200)

    def test_guest_links(self):
        """проверяет доступные ссылки для неавторизованного пользователя"""
        for link in self.guest_links:
            with self.subTest():
                response = self.guest_client.get(link)
                self.assertEqual(response.status_code, 200)

    def test_guest_links(self):
        """проверяет, что не зарегестрированный пользователь будет
        перенаправлен"""
        for link in self.guest_redirect_links:
            with self.subTest():
                response = self.guest_client.get(link)
                self.assertEqual(response.status_code, 302)

    def test_not_author_check_edit_link(self):
        """проверяет что авторизованный не автор , не сможет отредактировать
        пост , он будет перенаправлен на регистрацию"""
        self.authorized_client_not_author.force_login(self.user_test_2)
        response = self.authorized_client_not_author.get(reverse(
            'posts:post_edit', kwargs={'username': 'tester', 'post_id': '1'}))
        self.assertEqual(response.status_code, 302)

    def test_page_not_found(self):
        response = self.authorized_client.get('404/')
        self.assertEqual(response.status_code, 404)
