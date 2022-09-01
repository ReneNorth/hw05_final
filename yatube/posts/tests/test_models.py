from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Post, Group


User = get_user_model()


class PostTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='test_title_1',
            slug='test_slug_1',
            description='test_desc_1',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Sed ut perspiciatis unde omnis iste natus error sit'
        )

    def test_str_post(self):
        """ MODELS | Тест вывод 15 символов поста """
        test_post = PostTest.post
        max_len = 15
        text_len = len(str(test_post))
        self.assertEqual(text_len, max_len)

    def test_group_titile(self):
        """ MODELS | Тест совпадения title """
        test_group = PostTest.group
        expected_group_name = test_group.title
        self.assertEqual(expected_group_name, str(test_group))

    def test_verbose_name(self):
        """ MODELS | Тест соответствия vebose name """
        help_texts_dict = {
            'text': 'Текст поста',
            'group': 'Название группы',
        }
        for field, verbose in help_texts_dict.items():
            with self.subTest(field=field):
                verbose_test = PostTest.post._meta.get_field(field
                                                             ).verbose_name
                self.assertEqual(verbose, verbose_test)

    def test_help_text(self):
        """ MODELS | Тест соответствия help text"""
        help_texts_dict = {
            'text': 'Текстовое поле текст пост',
            'group': 'Это группы',
        }
        for field, text in help_texts_dict.items():
            with self.subTest(field=field):
                help_text_test = PostTest.post._meta.get_field(field).help_text
                self.assertEqual(text, help_text_test)
