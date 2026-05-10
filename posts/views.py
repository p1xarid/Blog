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

    form = CommentForm()

    if request.method == "POST":
        if "delete_comment" in request.POST:
            comment_id = request.POST.get("comment_id")
            comment = get_object_or_404(Comment, id=comment_id)

            if request.user == comment.author or request.user == post.author:
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

    return render(
        request,
        "posts/post_detail.html",
        {"post": post, "form": form, "comment_count": comments_count},
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

    if post.author != request.user:
        raise Http404("You don't have permission to edit this post")

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)

        if form.is_valid():
            post = form.save(commit=False)
            post.status = request.POST.get("status")
            post.save()

            return redirect("post_detail", slug=post.slug)

    else:
        form = PostForm(instance=post)

    return render(request, "posts/post_create.html", {"form": form, "is_edit": True})
