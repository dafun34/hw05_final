from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name='Название группы',
        max_length=200,
        help_text='Придумайте название для группы',
        unique=True
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Здесь расскажите про что ваша группа'
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        help_text=('Укажите адрес для страницы группы. Используйте только'
                   ' латиницу, цифры, дефисы и знаки подчеркивания'),
        unique=True,
        blank=True,
        max_length=100

    )

    def __str__(self):
        return self.title[:15]

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.title[:100]
        super().save(*args, **kwargs)


class Post(models.Model):
    text = models.TextField(verbose_name='Текст',
                            help_text='Напишите здесь что-либо'
                            )
    pub_date = models.DateTimeField(verbose_name='Дата публикации',
                                    help_text=('Дата публикации. Добавляется'
                                               ' автоматически'),
                                    auto_now_add=True,
                                    db_index=True
                                    )
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор',
                               help_text=('Здесь необходимо выбрать автора'
                                          ' публикации')
                               )
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True,
                              null=True, related_name='posts',
                              verbose_name='Группа',
                              help_text=('Здесь можно выбрать группу для '
                                         'публикации')
                              )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return self.text[:15]

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date'][:12]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')



