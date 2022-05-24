from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def paginator(request, post_list, page_per_list):
    paginator = Paginator(post_list, page_per_list)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    PAGE_PER_LIST = 10
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    post_list = Post.objects.select_related('author', 'group').all()
    page_obj = paginator(request, post_list, PAGE_PER_LIST)
    context = {
        'title': title,
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    PAGE_PER_LIST = 10
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author', 'group').all()
    page_obj = paginator(request, post_list, PAGE_PER_LIST)
    context = {
        'title': group.title,
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):
    PAGE_PER_LIST = 10
    template = 'posts/profile.html'
    title = f'Профайл пользователя {username}'
    author = get_object_or_404(User, username=username)
    fio = author.get_full_name
    post_author = author.posts.select_related('author', 'group').all()
    count = post_author.count()
    page_obj = paginator(request, post_author, PAGE_PER_LIST)
    context = {
        'title': title,
        'author': author,
        'post_author': post_author,
        'page_obj': page_obj,
        'fio': fio,
        'count': count
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    count = Post.objects.filter(author=post.author).count()
    title = 'Детали поста'
    context = {
        'post': post,
        'count': count,
        'title': title
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    title = 'Новый пост'
    form = PostForm()
    context = {
        'form': form,
        'title': title,
        'is_edit': False
    }
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user)
        return render(request, template, context)
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post.id)
    form = PostForm(instance=post)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
        return redirect('posts:post_detail', post_id=post.id)
    template = 'posts/create_post.html'
    context = {
        'form': form,
        'is_edit': True,
        'post_id': post.id
    }
    return render(request, template, context)
