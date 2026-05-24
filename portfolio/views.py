from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect, render, get_object_or_404
from portfolio.forms import EmailUpdateForm, UsernameUpdateForm, PasswordUpdateForm
from portfolio.models import Portfolio, Subscribe, FriendRequest
from posts.models import Post


@login_required
def portfolio(request, username):
    user = get_object_or_404(User, username=username)
    portfolio, _ = Portfolio.objects.get_or_create(user=user)
    posts = Post.objects.filter(author=portfolio.user)

    posts_count = posts.count()
    posts_published = Post.objects.filter(
        status="published", author=portfolio.user
    ).count()

    total_rating = 0

    for post in posts:
        likes_count = post.likes.count() if hasattr(post, "likes") else 0
        dislikes_count = post.dislikes.count() if hasattr(post, "dislikes") else 0

        if dislikes_count:
            total_rating += likes_count / dislikes_count
        else:
            total_rating += likes_count

    avg_rating = total_rating / posts_count if posts_count > 0 else 0

    subscriber_count = Subscribe.objects.filter(portfolio=portfolio).count()
    is_subscribed = Subscribe.objects.filter(
        portfolio=portfolio, user=request.user
    ).exists()

    if request.method == "POST":
        if "subscribe" in request.POST:
            if is_subscribed:
                Subscribe.objects.filter(
                    portfolio=portfolio, user=request.user
                ).delete()
            else:
                Subscribe.objects.create(portfolio=portfolio, user=request.user)

            return redirect("users_portfolio", username=username)

    return render(
        request,
        "profile/portfolio.html",
        {
            "portfolio": portfolio,
            "subscriber_count": subscriber_count,
            "is_subscribed": is_subscribed,
            "avg_rating": avg_rating,
            "posts_count": posts_count,
            "posts_published": posts_published,
        },
    )


@login_required
def my_portfolio(request):
    portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
    posts = Post.objects.filter(author=request.user).order_by("-created_at")

    posts_count = posts.count()
    total_rating = 0

    for post in posts:
        likes_count = post.likes.count() if hasattr(post, "likes") else 0
        dislikes_count = post.dislikes.count() if hasattr(post, "dislikes") else 0

        if dislikes_count:
            total_rating += likes_count / dislikes_count
        else:
            total_rating += likes_count

    avg_rating = total_rating / posts_count if posts_count > 0 else 0
    subscriber_count = Subscribe.objects.filter(portfolio=portfolio).count()

    return render(
        request,
        "profile/my_portfolio.html",
        {
            "portfolio": portfolio,
            "posts": posts,
            "posts_count": posts_count,
            "avg_rating": avg_rating,
            "subscriber_count": subscriber_count,
        },
    )


@login_required
def friends(request):
    portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
    friends = portfolio.friends.all()
    search_query = request.GET.get("q", "").strip()
    search_results = []

    incoming_requests = FriendRequest.objects.filter(
        to_user=request.user, accepted=False
    )
    outgoing_requests = FriendRequest.objects.filter(
        from_user=request.user, accepted=False
    )

    if request.method == "POST":
        if "send_request" in request.POST:
            username = request.POST.get("username")
            if username:
                to_user = (
                    User.objects.filter(username=username)
                    .exclude(pk=request.user.pk)
                    .first()
                )
                if to_user and not portfolio.friends.filter(pk=to_user.pk).exists():
                    existing_request = FriendRequest.objects.filter(
                        from_user=to_user, to_user=request.user, accepted=False
                    ).first()
                    if existing_request:
                        existing_request.accepted = True
                        existing_request.save()
                        portfolio.friends.add(to_user)
                        friend_portfolio, _ = Portfolio.objects.get_or_create(
                            user=to_user
                        )
                        friend_portfolio.friends.add(request.user)
                    else:
                        FriendRequest.objects.get_or_create(
                            from_user=request.user, to_user=to_user
                        )
            return redirect("friends")

        if "accept_request" in request.POST:
            request_id = request.POST.get("request_id")
            friend_request = FriendRequest.objects.filter(
                pk=request_id, to_user=request.user, accepted=False
            ).first()
            if friend_request:
                friend_request.accepted = True
                friend_request.save()
                portfolio.friends.add(friend_request.from_user)
                friend_author_portfolio, _ = Portfolio.objects.get_or_create(
                    user=friend_request.from_user
                )
                friend_author_portfolio.friends.add(request.user)
            return redirect("friends")

        if "decline_request" in request.POST:
            request_id = request.POST.get("request_id")
            FriendRequest.objects.filter(
                pk=request_id, to_user=request.user, accepted=False
            ).delete()
            return redirect("friends")

    if search_query:
        user_results = (
            User.objects.filter(username__icontains=search_query)
            .exclude(pk=request.user.pk)
            .order_by("username")[:20]
        )
        search_results = []
        for user_item in user_results:
            search_results.append(
                {
                    "user": user_item,
                    "is_friend": friends.filter(pk=user_item.pk).exists(),
                    "sent_request": outgoing_requests.filter(
                        to_user=user_item
                    ).exists(),
                    "received_request": incoming_requests.filter(
                        from_user=user_item
                    ).exists(),
                }
            )

    return render(
        request,
        "profile/friends.html",
        {
            "portfolio": portfolio,
            "friends": friends,
            "search_query": search_query,
            "search_results": search_results,
            "incoming_requests": incoming_requests,
            "outgoing_requests": outgoing_requests,
        },
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
