from django.urls import path
from .views import toggle_post_like

urlpatterns = [
    path("post/<slug:slug>/like/", toggle_post_like, name="toggle_post_like"),
]
