from django.contrib.auth.models import User
from django.db import models
from posts.models import Post
from posts.models import Comment


class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")


class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "comment")
