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
