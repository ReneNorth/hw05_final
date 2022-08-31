from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Post, Group
from http import HTTPStatus

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='test_group',
            slug='any_slug',
            description='test_description',
        )

        cls.post = Post.objects.create(
            text='test text first post',
            author=cls.user,
            group=cls.group,
        )
        cls.user2 = User.objects.create(username='nonauthor')
        cls.post2 = Post.objects.create(
            text='test text second post',
            author=cls.user2,
            group=cls.group,
        )

    def setUp(self):
        # неавторизованный клиент
        self.guest_client = Client()

        # авторизованный клиент-автор поста
        self.user = User.objects.get(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        # авторизованный клиент-не-автор поста
        self.user2 = User.objects.get(username='nonauthor')
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_urls_authorized_author(self):
        """ URLS | Тестируем совпадение URL и вызываемого шаблона """
        template_url_names = {
            '/': 'posts/index.html',
            '/group/any_slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/post_create.html',
            '/create/': 'posts/post_create.html',
            '/about/tech/': 'about/tech.html',
            '/about/author/': 'about/author.html',
        }
        for address, template in template_url_names.items():
            with self.subTest(address=address, template=template):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_not_authorized(self):
        template_url_names = {
            '/group/any_slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/about/tech/': 'about/tech.html',
            '/about/author/': 'about/author.html',
            '/posts/1/': 'posts/post_detail.html',
        }
        for address, template in template_url_names.items():
            with self.subTest(address=address, template=template):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_non_author_access_edit(self):
        """ URLS | Тестируем, что пользователь не может
        редактировать пост другого автора """
        response = self.authorized_client2.get('/posts/1/edit')
        self.assertEqual(response.status_code, HTTPStatus.MOVED_PERMANENTLY)

    def test_404_works(self):
        """ URLS | Тестируем 404 при вызове несуществующего адреса """
        non_exist_page = '/unexisting_page/'
        response = self.guest_client.get(non_exist_page)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response = self.authorized_client.get(non_exist_page)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_about_url_exists_at_desired_location(self):
        """ Тест страниц tech/author """
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
