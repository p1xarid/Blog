from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from posts.forms import PostForm
from posts.models import Post
from django.http import Http404


def post_list(request):
    posts = Post.objects.filter(status="published").order_by("-created_at")

    return render(request, "posts/post_list.html", {"posts": posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status="published")

    if post.status == "draft" and post.author != request.user:
        raise Http404("Post not found")

    return render(request, "posts/post_detail.html", {"slug": slug, "post": post})


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
