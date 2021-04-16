import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.forms import PostForm
from posts.models import Post, Group

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
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
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            description='Описание',
            slug='test'
        )
        cls.form_data = {
            'text': 'Текст из формы',
            'author': cls.test_user,
            'group': cls.test_group.id,
            'image': cls.uploaded
        }
        # Создаем запись в базе данных
        cls.test_post = Post.objects.create(
            text='Тестовый текст',
            author=cls.test_user,
            group=cls.test_group,

        )

        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = self.test_user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_text_label(self):
        text_label = self.form.fields['text'].label
        self.assertEqual(text_label, 'Текст:')

    def test_text_help(self):
        text_help = self.form.fields['text'].help_text
        self.assertEqual(text_help, 'В верхнее поле можно написать текст')

    def test_create_post(self):
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=self.form_data,
            follow=True
        )
        self.assertEqual(posts_count + 1, Post.objects.count())
        self.assertRedirects(response, reverse('posts:index'))
        self.assertTrue(
            Post.objects.filter(
                text='Текст из формы',
                image='posts/small.gif'
            ).exists()
        )

    def test_username_post_edit(self):
        """Проверяет что запись изменяется, а не публикуется новая """
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
            'group': self.test_group.id
        }
        response = self.authorized_client.post(reverse(
            'posts:post_edit', kwargs={'username': 'tester', 'post_id': '1'}),
            data=form_data,
            follow=True
        )
        self.assertEqual(post_count, Post.objects.count())
        self.assertRedirects(response, reverse(
            'posts:post', kwargs={'username': 'tester', 'post_id': '1'}))
