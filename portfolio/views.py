from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect, render, get_object_or_404
from portfolio.forms import EmailUpdateForm, UsernameUpdateForm, PasswordUpdateForm
from portfolio.models import Portfolio
from posts.models import Post


@login_required
def portfolio(request, username):
    user = get_object_or_404(User, username=username)
    portfolio, _ = Portfolio.objects.get_or_create(user=user)

    return render(
        request,
        "profile/portfolio.html",
        {"portfolio": portfolio},
    )


@login_required
def my_portfolio(request):
    portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
    posts = Post.objects.filter(author=request.user).order_by("-created_at")

    return render(
        request,
        "profile/my_portfolio.html",
        {"portfolio": portfolio, "posts": posts},
    )


@login_required
def portfolio_settings(request):
    portfolio, _ = Portfolio.objects.get_or_create(user=request.user)

    if request.method == "POST":
        if "reset_avatar" in request.POST:
            portfolio.avatar.delete(save=False)
            portfolio.avatar.name = ""
            portfolio.save()
            return redirect("portfolio_settings")

        if "avatar" in request.FILES:
            portfolio.avatar = request.FILES["avatar"]
            portfolio.save()
            return redirect("portfolio_settings")

        if "update_bio" in request.POST:
            portfolio.bio = request.POST["bio"]
            portfolio.save()
            return redirect("portfolio_settings")

    return render(
        request,
        "profile/portfolio_settings.html",
        {
            "portfolio": portfolio,
        },
    )


@login_required
def portfolio_update(request):
    portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
    username_form = UsernameUpdateForm()
    email_form = EmailUpdateForm()
    password_form = PasswordUpdateForm(user=request.user)

    if request.method == "POST":
        if "update_username" in request.POST:
            username_form = UsernameUpdateForm(request.POST)
            if username_form.is_valid():
                request.user.username = username_form.clean_username()
                request.user.save()
                return redirect("portfolio_update")

        elif "update_email" in request.POST:
            email_form = EmailUpdateForm(request.POST)
            if email_form.is_valid():
                request.user.email = email_form.clean_email()
                request.user.save()
                return redirect("portfolio_update")

        elif "update_password" in request.POST:
            password_form = PasswordUpdateForm(request.user, request.POST)
            if password_form.is_valid():
                request.user.set_password(password_form.cleaned_data["new_password"])
                request.user.save()
                update_session_auth_hash(request, request.user)
                return redirect("portfolio_update")

        elif "delete_account" in request.POST:
            request.user.delete()
            return redirect("home")

    return render(
        request,
        "profile/portfolio_update.html",
        {
            "portfolio": portfolio,
            "username_form": username_form,
            "email_form": email_form,
            "password_form": password_form,
        },
    )
