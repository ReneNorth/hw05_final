from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст вашего поста',
            'group': 'Группа',
            'image': 'Изображение',
        }
        help_texts = {
            'text': 'Начните писать! Вдохновение придёт со временем.',
            'group': 'Пост будет относится к выбранной группе',
            'image': 'Загрузите изображение к посту',
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Комментарий'}
        help_texts = {'text': 'Ваш комментарий к посту'}