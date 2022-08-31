from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, Follow
from .forms import PostForm, CommentForm
from yatube.settings import DEF_NUM_POSTS
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.views.decorators.cache import cache_page


User = get_user_model()


def paginator(list_of_posts, request):
    paginator = Paginator(list_of_posts, DEF_NUM_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(1 * 20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.all().select_related('author', 'group')
    page_obj = paginator(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all().select_related('author', 'group')
    page_obj = paginator(post_list, request)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all().select_related('group')
    page_obj = paginator(post_list, request)
    if request.user.id == author.id:
        context = {
            'page_obj': page_obj,
            'author': author,
            'failed': 'Нельзя подписаться на самого себя!',
        }
        return render(request, 'posts/profile.html', context)
    else:
        if request.user.is_authenticated:
            check = Follow.objects.all().filter(
                user_id=request.user,
                author_id=author
            )
            if not check:
                follow = False
            else:
                follow = True
            context = {
                'page_obj': page_obj,
                'author': author,
                'following': follow,
            }
            return render(request, 'posts/profile.html', context)
        context = {
            'page_obj': page_obj,
            'author': author,
            'failed': 'failed',
        }
        return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comment_list = post.comments.all()
    form = CommentForm(
        request.POST or None,
    )
    context = {
        'post': post,
        'comments': comment_list,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('posts:profile', post.author)
        return render(request, 'posts/post_create.html', {'form': form})
    return render(request, 'posts/post_create.html',
                  {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'post_id': post_id,
        'is_edit': is_edit,
    }
    return render(request, 'posts/post_create.html', context)


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
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user.id != author.id and not Follow.objects.all().filter(
            user=request.user,
            author=author
    ):
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    unfollowing_author = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=unfollowing_author).delete()
    return redirect('posts:profile', username=unfollowing_author)
