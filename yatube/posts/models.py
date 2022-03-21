from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F, Q

User = get_user_model()


class Group(models.Model):
    '''Модель сообщества (группы) содержит поля:
    - title - название сообщества;
    - slug - уникальный url адрес страницы сообщества;
    - description - описание сообщества;
    - функция __str__ переопределена и показывает название сообщества title.
    '''
    title = models.CharField(settings.GROUP_NAME, max_length=200)
    slug = models.SlugField(settings.URL_NAME, unique=True)
    description = models.TextField(settings.DESCRIPTION_NAME)

    class Meta:
        verbose_name = settings.GROUP_NAME
        verbose_name_plural = settings.GROUPS_NAME

    def __str__(self):
        return(self.title)


class Post(models.Model):
    '''Модель сообщения содержит поля:
    - text - текст сообщения;
    - pub_date - дата публикации, по-умолчанию текущая;
    - author - автор (при удалении автора удаляются все сообщения)
    - group - сообщество (группа) куда написаны посты, опционально.
    '''
    text = models.TextField(settings.TEXT_NAME)
    pub_date = models.DateTimeField(settings.DATE_NAME, auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name=settings.AUTHOR_NAME
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name=settings.GROUP_NAME
    )

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = settings.POST_NAME
        verbose_name_plural = settings.POSTS_NAME

    def __str__(self):
        return(f'{self.text[:15]}')


class Comment(models.Model):
    '''Модель комментария содержит поля:
    - text - текст комментария;
    - created - дата публикации, по-умолчанию текущая;
    - author - автор (при удалении автора удаляются все сообщения)
    - post - сообщение для которого написаны комментарии.
    '''
    text = models.TextField(settings.COMMENT_NAME)
    created = models.DateTimeField(settings.DATE_NAME, auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=settings.AUTHOR_NAME
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=settings.TEXT_NAME,
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = settings.COMMENT_NAME
        verbose_name_plural = settings.COMMENTS_NAME

    def __str__(self):
        return(f'{self.text[:15]}')


class Follow(models.Model):
    '''Модель подписки содержит поля:
    - user - подписчик;
    - author - автор интересующий подписчика.
    '''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name=settings.AUTHOR_NAME,
        null=True
    )

    class Meta:
        ordering = ('-author',)
        verbose_name = settings.FOLLOW_NAME
        verbose_name_plural = settings.FOLLOWS_NAME
        constraints = [
            models.CheckConstraint(check=~Q(user=F('author')),
                                   name='disable_self-following'),
            models.UniqueConstraint(fields=('user', 'author'),
                                    name='unique_following')
        ]

    def __str__(self):
        return(f'{self.user} => {self.author}')
