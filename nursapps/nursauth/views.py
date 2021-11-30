"""Nursauth views module."""
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from nursapps.agenda.models import Associate, Cabinet, RequestAssociate
from nursapps.nursauth.models import User
from .forms import (
    InscriptForm,
    NewLoginForm,
)
from nursapps.cabinet.forms import (
    CreateCabinet,
    AssociationValidation,
)


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


@login_required
def user_profile(request):
    """Account."""
    sender = None
    associate = None
    lst_associates_id = None
    cab_id = None
    cab_name = None

    cab_form = CreateCabinet(request.POST)
    valid_form = AssociationValidation(request.POST)
    association_request = RequestAssociate.objects.filter(receiver_id=request.user.id)
    assreq = association_request.values_list("sender_id", flat=True)

    sender_request = RequestAssociate.objects.filter(sender_id=request.user.id)
    if assreq:
        sender = User.objects.filter(pk__in=[i for i in assreq])
    associate = Associate.objects.filter(user_id=request.user.id)
    associate = associate.first()
    # breakpoint()

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
    }
    return render(request, "registration/profile.html", context)
