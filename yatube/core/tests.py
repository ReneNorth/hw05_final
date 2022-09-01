from http import HTTPStatus

from django.test import TestCase, Client


class ViewTestClass(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_error_page(self):
        non_page = '/nonexist-page/'
        template = 'core/404.html'

        response = self.client.get(non_page)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(self.guest_client.get(non_page), template)
