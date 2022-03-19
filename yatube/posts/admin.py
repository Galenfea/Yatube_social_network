from django.conf import settings
from django.contrib import admin

from .models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    '''Источник конфигурации модели Post, регистрируемой в админке, позволяет:
    - отображать в админке первичный ключ, текст, дату публикации, автора и
    сообщество (группу) каждой записи;
    - редактировать поле сообщества (группы);
    - проводить поиск по тексту;
    - фильттровать по дате публицкации;
    - выводить "-пусто-" в полях со значением None.'''
    list_display = ('pk', 'text', 'pub_date', 'author', 'group', 'image')
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = settings.EMPTY


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    '''Источник конфигурации модели Group, регистрируемой в админке, позволяет:
    - отображать в админке первичный ключ, название сообщества, ссылку и
    описание сообщества;
    - редактировать название и описание сообщества;
    - проводить поиск по названию сообщества;
    - выводить "-пусто-" в полях со значением None.'''
    list_display = ('pk', 'title', 'slug', 'description',)
    list_editable = ('title', 'description')
    search_fields = ('title',)
    empty_value_display = settings.EMPTY


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    '''Источник конфигурации модели Comment, регистрируемой в админке, позволяет:
    - отображать в админке первичный ключ, текст комментария, дату создания,
    автора комментария;
    - редактировать текст комментария;
    - проводить поиск по тексту комментария;
    - выводить "-пусто-" в полях со значением None.'''
    list_display = ('pk', 'text', 'created', 'author', 'post',)
    list_editable = ('text',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = settings.EMPTY


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    '''Источник конфигурации модели Follow, регистрируемой в админке, позволяет:
    - отображать в админке первичный ключ, подписчика и
    автора, на которого происходит подписка;
    - удалять подписку;
    - проводить поиск по авторам и подписчикам;
    - выводить "-пусто-" в полях со значением None.'''
    list_display = ('pk', 'author', 'user',)
    search_fields = ('author', 'user',)
    empty_value_display = settings.EMPTY
