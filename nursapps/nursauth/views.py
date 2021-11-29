"""Nursauth view module."""
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required
from nursapps.agenda.models import Associate, Cabinet, RequestAssociate
from nursapps.nursauth.models import User
from .forms import (
    InscriptForm,
    NewLoginForm,
)

# from nursapps.cabinet.forms import (
#     CreateCabinet,
#     AssociationValidation,
# )


def inscript(request):
    """Inscript view."""
    if request.method == "POST":
        form = InscriptForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("profile")
    else:
        form = InscriptForm()
    return render(request, "registration/inscript.html", {"form_ins": form})


def login(request):
    """Login view."""
    if request.method == "POST":
        login_form = NewLoginForm(request.POST)
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user:
            auth_login(request, user)
            return redirect("profile")
    else:
        login_form = NewLoginForm()
    return render(
        request,
        "registration/login.html",
        {"login_form": login_form},
    )
