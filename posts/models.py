from django.db import models
from django.contrib.auth.models import User
from slugify import slugify
import uuid


class Post(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")

    def save(self, *args, **kwargs):
        unique_id = str(uuid.uuid4().hex[:8])
        if not self.slug:
            self.slug = slugify(self.title)[:50].rstrip("-") + "-" + unique_id
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def level(self):
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level

    def __str__(self):
        return f"{self.author} -> {self.post}"
