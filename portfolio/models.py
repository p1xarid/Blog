from django.db import models
from django.contrib.auth.models import User


class Portfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="pictures/", blank=True, null=True)
    bio = models.TextField(max_length=200, blank=True, null=True)

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return "/static/pictures/default-avatar.png"
