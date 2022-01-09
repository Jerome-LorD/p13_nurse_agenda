"""Nursauth views module."""
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from nursapps.cabinet.models import Associate, Cabinet, RequestAssociate
from nursapps.nursauth.models import User
from .forms import (
    InscriptForm,
    NewLoginForm,
)
from nursapps.cabinet.forms import (
    CreateCabinetForm,
    AssociationValidationForm,
    # DeclineAssociationForm,
)

from datetime import datetime

now = datetime.now()


def inscript(request):
    """Inscript view."""
    if request.method == "POST":
        form = InscriptForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return HttpResponseRedirect(
                reverse(
                    "nursauth:profile",
                )
            )
    else:
        form = InscriptForm()
    return render(
        request,
        "registration/inscript.html",
        {
            "form_ins": form,
            "current_month": now.month,
            "current_year": now.year,
        },
    )


def login(request):
    """Login view."""
    if request.method == "POST":
        form = NewLoginForm(request.POST)
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user:
            auth_login(request, user)
            messages.add_message(request, messages.SUCCESS, "Vous êtes connecté !")
            return HttpResponseRedirect(
                reverse(
                    "nursauth:profile",
                )
            )
        else:
            messages.add_message(
                request, messages.ERROR, "Les champs renseignés sont invalides."
            )
    else:
        form = NewLoginForm()
    return render(
        request,
        "registration/login.html",
        {
            "login_form": form,
            "current_month": now.month,
            "current_year": now.year,
        },
    )


@login_required
def user_profile(request):
    """Account."""
    context = {"current_month": now.month, "current_year": now.year}
    sender_request = RequestAssociate.objects.filter(sender_id=request.user.id)
    association_request = RequestAssociate.objects.filter(receiver_id=request.user.id)
    association_request = association_request.values_list("sender_id", flat=True)

    if association_request:
        sender = User.objects.filter(pk__in=[i for i in association_request])
        context["sender"] = sender
    associate = Associate.objects.filter(user_id=request.user.id)
    associate = associate.first()

    if sender_request.exists():
        context.update(user_send_request_for_association=sender_request)
    elif Associate.objects.filter(user=request.user).exists():
        associate = Associate.objects.get(user=request.user)
        if associate or request.user.is_cabinet_owner or sender_request or sender:
            associates = Associate.objects.get_associates(associate.cabinet.id)
            confirm_form = AssociationValidationForm(request.POST)
            context.update(
                associates=associates,
                user_send_request_for_association=sender_request,
                confirm_form=confirm_form,
            )
    else:
        return redirect("cabinet:create")

    return render(request, "registration/profile.html", context)
