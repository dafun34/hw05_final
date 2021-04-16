from django.test import Client, TestCase
from django.urls import reverse


class StaticUrlsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.urls = [
            'about:author',
            'about:tech'
        ]

    def test_about_urls(self):
        """страницы доступны гостю"""
        for url in self.urls:
            with self.subTest():
                response = self.guest_client.get(reverse(url))
                self.assertEqual(response.status_code, 200)
