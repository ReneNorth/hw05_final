from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from posts.models import Post, Group, Comment
from django.urls import reverse
from django.conf import settings
from posts.forms import PostForm, CommentForm
import shutil
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from http import HTTPStatus


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='test_group1',
            slug='any_slug1',
            description='test_description1',
        )
        cls.group2 = Group.objects.create(
            title='changed_test_group2',
            slug='changed_any_slug2',
            description='changed_test_description2',
        )

        cls.post = Post.objects.create(
            text='test text first post',
            author=cls.user,
            group=cls.group,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')

        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')

    def test_create_post(self):
        """ FORMS | Валидная форма создает новый пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': PostFormsTest.group.id
        }
        self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        self.assertTrue(Post.objects.filter(
            text='Тестовый текст',
            author__username='auth',
            group__slug='any_slug1',
        ).exists()
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_create_post_wpic(self):
        """ FORMS | Валидная форма с картинкой создает новый пост."""
        posts_count = Post.objects.count()
        form_data2 = {
            'text': 'Это пост с картинкой!',
            'image': self.uploaded,
        }
        self.authorized_client.post(
            reverse('posts:post_create'), data=form_data2, follow=True
        )
        self.assertTrue(
            Post.objects.latest('pub_date').image,
            f'posts/{self.uploaded.name}'
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """ FORMS | Проверка редактирования поста. """
        form_data = {
            'text': 'CHANGED Тестовый текст',
        }
        self.authorized_client.post(
            reverse(
                'posts:post_edit', args=(self.post.pk,)
            ), data=form_data, follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                pk=self.post.pk, text='CHANGED Тестовый текст'
            ).exists()
        )

    def test_edit_group(self):
        """ Тестируем, что после изменения группы
        поста нет на странице старой группы """
        form_data = {
            'text': 'also we changed the group',
            'group': PostFormsTest.group2.id,
        }
        self.authorized_client.post(
            reverse(
                'posts:post_edit', args=(self.post.pk,)
            ), data=form_data, follow=True
        )
        # запрашиваем страницу старой группы и считаем количество объектов,
        # должно быть 0
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_comments_post_page(self):
        """ FORMS | После успешного создания комментария
        текст появился на странице поста """
        form_data = {
            'text': 'test comment text'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    args={self.post.pk}), data=form_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.authorized_client.get(
            reverse('posts:post_detail', args={self.post.pk})
        )
        self.assertEqual(
            response.context['comments'][0].text,
            form_data['text'])

    def test_comments_access(self):
        """ FORMS | Только авторизованный пользователь
        может оставить комментарий """
        form_data = {
            'text': 'this comment should not appear on the page'
        }
        response = self.guest_client.post(
            reverse('posts:add_comment',
                    args={self.post.pk}), data=form_data, follow=True)
        response = self.authorized_client.get(
            reverse('posts:post_detail', args={self.post.pk})
        )
        # Проверяем, что на странице поста не появилось комментариев
        self.assertEqual(
            len(response.context['comments']), 0)
