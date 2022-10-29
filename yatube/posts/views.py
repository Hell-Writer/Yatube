from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment, Follow
from .utils import pagination


def index(request):
    posts = Post.objects.all()
    page_obj = pagination(request, posts, settings.VIEWABLE_POSTS)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = pagination(request, posts, settings.VIEWABLE_POSTS)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    user = request.user
    if user.is_authenticated:
        following = Follow.objects.filter(author=author, user=user).exists()
    else:
        following = False
    page_obj = pagination(request, posts, settings.VIEWABLE_POSTS)
    context = {
        'following': following,
        'author': author,
        'page_obj': page_obj
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = post.author
    comments = Comment.objects.filter(post=post)
    form = CommentForm(request.POST, request.FILES or None)
    context = {'post': post,
               'author': user,
               'comments': comments,
               'form': form}
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author_id = request.user.pk
        form.save()
        return redirect('posts:profile', username=request.user)
    context = {'form': form}
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(instance=post)
    if request.user != post.author:
        return redirect('posts:profile', username=request.user)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post': post
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = pagination(request, posts, settings.VIEWABLE_POSTS)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    switch = Follow.objects.filter(
        user=user,
        author=author).exists()
    if user != author and switch is False:
        Follow.objects.create(
            user=user,
            author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author=User.objects.get(username=username)).delete()
    return redirect('posts:profile', username=username)
