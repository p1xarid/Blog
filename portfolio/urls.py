from django.urls import path
from portfolio import views

urlpatterns = [
    path("", views.my_portfolio, name="my_portfolio"),
    path("update/", views.portfolio_update, name="portfolio_update"),
    path("settings/", views.portfolio_settings, name="portfolio_settings"),
    path("friends/", views.friends, name="friends"),
    path("<str:username>/", views.portfolio, name="users_portfolio"),
]
