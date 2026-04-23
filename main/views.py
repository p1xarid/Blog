from django.shortcuts import render

from portfolio.models import Portfolio


def home_view(request):
    portfolio = None
    if request.user.is_authenticated:
        portfolio, _ = Portfolio.objects.get_or_create(user=request.user)

    return render(request, "main/home.html", {"portfolio": portfolio})
