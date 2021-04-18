from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from posts.models import Post, Group, Follow
from posts.forms import PostForm, CommentForm
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/group.html', {'group': group, 'page': page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:index')
    return render(request, 'posts/new.html', {'form': form})


@login_required
def add_comment(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, id=post_id)
    form = CommentForm(request.POST or None)
    reverse_kwargs = {'username': username, 'post_id': post_id}
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(reverse('posts:post', kwargs=reverse_kwargs))


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_by_author = author.posts.filter(author=author)
    paginator = Paginator(posts_by_author, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if request.user.is_authenticated:
        authors = User.objects.filter(following__user=request.user)
        following = author in authors
        return render(request, 'posts/profile.html', {'author': author,
                                                      'page': page,
                                                      'following': following})
    return render(request, 'posts/profile.html', {'author': author,
                                                  'page': page})


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    posts_by_id = get_object_or_404(Post, author=author, id=post_id)
    form = CommentForm()
    comments = posts_by_id.comments.all()
    return render(request, 'posts/post.html', {'author': author,
                                               'post': posts_by_id,
                                               'form': form,
                                               'comments': comments})


@login_required
def post_edit(request, username, post_id):
    username = get_object_or_404(User, username=username)
    if request.user == username:
        post = get_object_or_404(Post, author=username, id=post_id)
        form = PostForm(request.POST or None,
                        files=request.FILES or None,
                        instance=post)
        if request.method == 'POST' and form.is_valid():
            form.save()
            return redirect(reverse('posts:post', kwargs={'username': username,
                                                          'post_id': post_id}))
        return render(request, 'posts/new.html', {'form': form,
                                                  'here': True,
                                                  'post': post})
    return redirect(reverse('posts:post', kwargs={'username': username,
                                                  'post_id': post_id}))


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def follow_index(request):
    user = request.user
    posts = Post.objects.filter(author__following__user=user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, "follow.html", {'page': page})


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect(reverse('posts:profile', args=[username]))


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=user, author=author)
    follow.delete()
    return redirect(reverse('posts:profile', args=[username]))
