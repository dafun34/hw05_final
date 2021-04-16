from django.test import TestCase
from posts.models import Post, Group
from django.contrib.auth import get_user_model

User = get_user_model()


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create_user(username='tester',
                                            email='testor@mail.ru',
                                            password='12345678'),)
        cls.group = Group.objects.create(
            title='title',
            description='Тестовое описание'
        )

    def test_text_convert_to_slug(self):
        """save преобразует в slug содержимое поля title."""
        group = GroupModelTest.group
        slug = group.slug
        self.assertEqual(slug, 'title')

    def test_object_is_title_name(self):
        group = GroupModelTest.group
        group_title = group.title[:15]
        self.assertEqual(group_title, str(group))

    def test_verbose_name(self):
        group = GroupModelTest.group
        verbose = group._meta.get_field('title').verbose_name
        self.assertEqual(verbose, 'Название группы')

    def test_help_text(self):
        group = GroupModelTest.group
        help_text = group._meta.get_field('title').help_text
        self.assertEqual(help_text, 'Придумайте название для группы')


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create_user(username='tester',
                                            email='testor@mail.ru',
                                            password='12345678'),
            group=Group.objects.create(title='Группа')
        )

    def test_verbose_name(self):
        """verbose_name поля text совпадает с ожидаемым."""
        post = PostModelTest.post
        verbose = post._meta.get_field('text').verbose_name
        self.assertEqual(verbose, 'Текст')

    def test_help_text(self):
        """help_text поля text совподает с ожидаемым. """
        post = PostModelTest.post
        help_text = post._meta.get_field('text').help_text
        self.assertEqual(help_text, 'Напишите здесь что-либо')

    def test_object_name_is_text_field(self):
        """__str__  post - это строчка с содержимым post.title."""
        post = PostModelTest.post
        post_text = post.text[:15]
        self.assertEqual(post_text, str(post))

    def test_author_name(self):
        """ author это username"""
        post = PostModelTest.post
        username = post.author.username
        self.assertEqual(username, 'tester')
