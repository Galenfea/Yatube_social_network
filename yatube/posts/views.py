# posts/views.py
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def posts_paginator(request, posts, context):
    '''Функция добавляет в контекст паджинатор для
    функциий index, group_posts и profile.
    '''
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = page_obj
    return context


def index(request):
    '''Функция отображения главной страницы, выводит 10 сообщений,
    отсортированных по дате от большей к меньшей,
    переменная template содержит путь к отображаемому шаблону html.
    '''
    template = 'posts/index.html'
    posts = Post.objects.all()
    context = {}
    context = posts_paginator(request, posts, context)
    return render(request, template, context)


def group_posts(request, slug):
    '''Функция отображения страницы сообщества (группы), выводит 10 сообщений
    сообщества (группы),  отсортированных по дате от большей к меньшей,
    переменная template содержит путь к отображаемому шаблону html.
    '''
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {'group': group}
    context = posts_paginator(request, posts, context)
    return render(request, template, context)


def profile(request, username):
    '''Функция выводит все сообщения пользователя.'''
    template = 'posts/profile.html'
    author = get_object_or_404(get_user_model(), username=username)
    posts = author.posts.all()
    following = False
    if request.user.is_authenticated:
        # Вложенное условие потому, что
        # в случае неавторизованного пользователя при фильтрации
        # возникает ошибка, поскольку аноним не является Queryset
        if Follow.objects.filter(user=request.user, author=author).exists():
            following = True
    context = {'author': author,
               'following': following
               }
    context = posts_paginator(request, posts, context)
    return render(request, template, context)


def post_detail(request, post_id):
    '''Функция выводит подробности о сообщении, в том числе и
    кнопку "редактировать".
    '''
    template = 'posts/post_detail.html'
    post = Post.objects.get(pk=post_id)
    author = get_object_or_404(get_user_model(), id=post.author_id)
    comment_form = CommentForm(request.POST or None)
    if post.group_id is None:
        group_name = ''
    else:
        group_name = Group.objects.get(pk=post.group_id).title
    context = {'post': post,
               'author': author,
               'group_name': group_name,
               'form': comment_form
               }
    return render(request, template, context)


@login_required
def post_create(request):
    '''Функция создаёт новое сообщение.'''
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None,
                    files=request.FILES or None
                    )
    context = {'form': form}
    if request.method == 'POST' and form.is_valid():
        # Экземпляр подготовленной, но не сохранённой, модели,
        # чтобы отредактировать её и добавить пользователя.
        instance_form = form.save(commit=False)
        instance_form.author = request.user
        instance_form.save()
        return redirect('posts:profile', request.user.username)
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    '''Функция редактирует сообщение пользователя.'''
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        form = PostForm(request.POST or {'text': post.text,
                        'group': post.group}, files=request.FILES or None,
                        instance=post
                        )
        if request.method == 'POST' and form.is_valid():
            post.text = form.cleaned_data['text']
            post.group = form.cleaned_data['group']
            form = PostForm(request.POST, instance=post)
            post.save()
            return redirect('posts:post_detail', post_id)
        context = {'form': form,
                   'post_id': post_id,
                   'is_edit': True,
                   }
        return render(request, template, context)
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, id=post_id)
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    '''Функция демонстрирует ленту постов от авторов,
    на которых подписан пользователь.'''
    # Функция используется при переходе 'follow/'
    context = {}
    template = 'posts/follow.html'
    # Берутся посты авторов, для которых в базе данных есть запись в таблице
    # posts_follow, но только тех из них, в чьих записях есть соответствие
    # текущему пользователю
    posts = Post.objects.filter(author__following__user=request.user)
    context = posts_paginator(request, posts, context)
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    '''Функция осуществляет подписку на автора, предположительно
    со страницы профиля автора.'''
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=user, author=author).delete()
    return redirect('posts:profile', username=username)
