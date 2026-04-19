from django.urls import path
from main import views
from . import views


urlpatterns = [
    path("", views.post_list, name="post_list"),
    path("create/", views.post_create, name="post_create"),
    path("<slug:slug>/", views.post_detail, name="post_detail"),
]
