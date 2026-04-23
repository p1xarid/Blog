from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


def register_view(request):
    error = None
    if request.method == "POST":
        email = request.POST.get("email", "")
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        if not email or not username or not password:
            error = "All fields are required!"

        elif User.objects.filter(username=username).exists():
            error = "This name is already registered!"

        elif User.objects.filter(email=email).exists():
            error = "This email is already registered!"

        else:
            User.objects.create_user(email=email, username=username, password=password)
            return redirect("login")

    return render(request, "account/register.html", {"error": error})


def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        if not username or not password:
            error = "Please enter a username and password!"
        else:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect("/")
            else:
                error = "Incorrect username or password!"

    return render(request, "account/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("login")
