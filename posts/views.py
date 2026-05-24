from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from posts.forms import PostForm, CommentForm
from posts.models import Post, Comment
from django.http import Http404
from rest_framework import generics
from .serializers import PostSerializer
from django.db.models import Count


class PostListAPI(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


def post_list(request):
    posts = Post.objects.filter(status="published").order_by("-created_at")
    return render(request, "posts/post_list.html", {"posts": posts})


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.annotate(comments_count=Count("comments")),
        slug=slug,
        status="published",
    )

    if post.status == "draft" and post.author != request.user:
        raise Http404("Post not found")

    if post.status == "friends":
        if (
            not request.user.is_authenticated
            or request.user not in post.author.portfolio.friends.all()
        ):
            raise Http404()

    form = CommentForm()

    if request.method == "POST":
        if "delete_post" in request.POST:
            if request.user == post.author or request.user.is_superuser:
                post.delete()
                return redirect("post_list")
            else:
                raise Http404("You don't have permission to delete this post")

        if "delete_comment" in request.POST:
            comment_id = request.POST.get("comment_id")
            comment = get_object_or_404(Comment, id=comment_id)

            if (
                request.user == comment.author
                or request.user == post.author
                or request.user.is_superuser
            ):
                comment.delete()

            return redirect("post_detail", slug=slug)

        if not request.user.is_authenticated:
            return redirect("login")

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user

            parent_id = request.POST.get("parent_id")

            if parent_id:
                parent_comment = get_object_or_404(Comment, id=parent_id)

                if parent_comment.level() < 4:
                    comment.parent = parent_comment

            comment.save()
            return redirect("post_detail", slug=slug)

    comments_count = post.comments.count()

    is_liked = False
    if request.user.is_authenticated:
        is_liked = post.likes.filter(id=request.user.id).exists()

    is_disliked = False
    if request.user.is_authenticated:
        is_disliked = post.dislikes.filter(id=request.user.id).exists()

    return render(
        request,
        "posts/post_detail.html",
        {
            "post": post,
            "form": form,
            "comment_count": comments_count,
            "is_liked": is_liked,
            "is_disliked": is_disliked,
        },
    )


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.status = request.POST.get("status")
            post.save()

            return redirect("post_detail", slug=post.slug)

    else:
        form = PostForm()

    return render(request, "posts/post_create.html", {"form": form})


@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if post.author != request.user and not request.user.is_superuser:
        raise Http404("You don't have permission to edit this post")

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)

        if form.is_valid():
            post = form.save(commit=False)
            post.status = request.POST.get("status")
            post.save()

            return redirect("my_portfolio")

    else:
        form = PostForm(instance=post)

    return render(request, "posts/post_create.html", {"form": form, "is_edit": True})
