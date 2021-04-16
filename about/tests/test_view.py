from django.test import Client, TestCase
from django.urls import reverse


class StaticUrlsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.urls = [
            'about:author',
            'about:tech'
        ]
        self.templates_and_urls = {
            'about/author.html': 'about:author',
            'about/tech.html': 'about:tech'
        }

    def test_about_urls(self):
        """страницы доступны гостю"""
        for url in self.urls:
            with self.subTest():
                response = self.guest_client.get(reverse(url))
                self.assertEqual(response.status_code, 200)

    def test_about_templates(self):
        """проверка шаблонов приложения about"""
        for template, link in self.templates_and_urls.items():
            with self.subTest():
                response = self.guest_client.get(reverse(link))
                self.assertTemplateUsed(response, template)
