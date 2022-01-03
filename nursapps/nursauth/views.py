"""Nursauth views module."""
from django.shortcuts import render
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
    CreateCabinet,
    AssociationValidation,
)

from datetime import datetime


def inscript(request):
    """Inscript view."""
    now = datetime.now()
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
    now = datetime.now()
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
    """Account.

    request.session["cabinet_name"] = cabinet.name


    """
    sender = None
    associate = None
    lst_associates_id = None
    cab_id = None
    cab_name = None
    now = datetime.now()

    cab_form = CreateCabinet(request.POST)
    valid_form = AssociationValidation(request.POST)
    association_request = RequestAssociate.objects.filter(receiver_id=request.user.id)
    assreq = association_request.values_list("sender_id", flat=True)

    sender_request = RequestAssociate.objects.filter(sender_id=request.user.id)
    if assreq:
        sender = User.objects.filter(pk__in=[i for i in assreq])
    associate = Associate.objects.filter(user_id=request.user.id)
    associate = associate.first()

    if associate:
        # obtains the list of identifiers of the partners of a firm in order to display
        # their names in the table of the profile page.
        lst_associates_id = Associate.objects.get_associates(associate.cabinet_id)
        cab_id = associate.cabinet_id
        cabinet = Cabinet.objects.filter(pk=cab_id).first()
        cab_name = cabinet.name

    else:
        cab_form = CreateCabinet()
        valid_form = AssociationValidation()

    context = {
        "first_name": request.user.username,
        "cab_form": cab_form,
        "valid_form": valid_form,
        "cab": associate,
        "sender": sender,
        "associates": lst_associates_id,
        "cab_id": cab_id,
        "cab_name": cab_name,
        "reqass": sender_request,
        "current_year": now.year,
        "current_month": now.month,
    }
    return render(request, "registration/profile.html", context)
