from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Текст нового поста',
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Автор поста'
    )
    group = models.ForeignKey(
        Group,
        related_name='posts',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text='Группа, к которой будет относиться пост',
        verbose_name='Группа'
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.text[:15]
