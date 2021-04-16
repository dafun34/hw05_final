from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': _('Текст:'),
            'group': _('Выберете группу:')
        }
        help_texts = {
            'text': _('В верхнее поле можно написать текст')
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': _('Текст')}
        help_texts = {'text': _('Напишите здесь комментарий')}
        widgets = {
            'text': forms.Textarea(attrs={'cols': 60, 'rows': 6})
        }