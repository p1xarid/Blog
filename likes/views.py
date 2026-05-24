from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from posts.models import Post
from .models import PostDislike, PostLike


@login_required
def toggle_post_like(request, slug):
    post = get_object_or_404(Post, slug=slug)

    like = PostLike.objects.filter(user=request.user, post=post)
    dislike = PostDislike.objects.filter(user=request.user, post=post)

    if like.exists():
        like.delete()
    else:
        dislike.delete()
        PostLike.objects.create(user=request.user, post=post)

    return redirect("post_detail", slug=slug)


@login_required
def toggle_post_dislike(request, slug):
    post = get_object_or_404(Post, slug=slug)

    dislike = PostDislike.objects.filter(user=request.user, post=post)
    like = PostLike.objects.filter(user=request.user, post=post)

    if dislike.exists():
        dislike.delete()
    else:
        like.delete()
        PostDislike.objects.create(user=request.user, post=post)

    return redirect("post_detail", slug=slug)
