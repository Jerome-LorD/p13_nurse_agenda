"""Cabinet module."""
from django.views.decorators.vary import vary_on_headers
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from nursapps.cabinet.models import Associate, Cabinet, RequestAssociate
from nursapps.nursauth.models import User
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from nursapps.cabinet.forms import (
    CreateCabinet,
    SearchForCabinet,
    AssociationValidation,
)

from django.http.response import (
    Http404,
    JsonResponse,
)

from datetime import datetime

now = datetime.now()


@vary_on_headers("User-Agent")
def autocomplete(request):
    """Jquery autocomplete response."""
    if request.method == "GET":
        cabinet = request.GET.get("term", "")
        cabinets = Cabinet.objects.filter(name__icontains="%s" % cabinet).order_by(
            "id"
        )[:10]
    return JsonResponse([{"name": cabinet.name} for cabinet in cabinets], safe=False)


def create_new_cabinet(request):
    """Create new cabinet."""
    sender = None
    new_cabinet = None
    associate = None
    cab_id = None
    cab_name = None
    association_request = RequestAssociate.objects.filter(receiver_id=request.user.id)
    assreq = association_request.values_list("sender_id", flat=True)
    RequestAssociate.objects.filter(sender_id=request.user.id)

    if assreq:
        sender = User.objects.filter(pk__in=[i for i in assreq])
    associate = Associate.objects.filter(user_id=request.user.id)
    associate = associate.first()
    if associate:
        # retrieves the list of IDs of a firm's partners in order to display their
        # names in the table on the profile page.
        lst_associates_id = Associate.objects.get_associates(associate.id)
        cab_id = associate.cabinet_id
        cabinet = Cabinet.objects.filter(pk=cab_id).first()
        cab_name = cabinet.name

    form = CreateCabinet(request.POST)
    if request.method == "POST":
        cabinet = request.POST.get("cabinet")
        if form.is_valid():
            try:
                cabin = Cabinet.objects.get(name=cabinet)
                if not request.user.is_cabinet_owner:
                    return HttpResponseRedirect(reverse("cabinet:askfor"))
                return HttpResponseRedirect(
                    reverse(
                        "nursauth:profile",
                    )
                )
            except Cabinet.DoesNotExist:
                cabinet = Cabinet.objects.create(name=cabinet)
                request.user.is_cabinet_owner = True
                request.user.save()
                associate = Associate.objects.create(
                    cabinet_id=cabinet.id, user_id=request.user.id
                )
                new_cabinet = cabinet.name
                return HttpResponseRedirect(
                    reverse(
                        "nursauth:profile",
                    )
                )

    context = {
        "cab_form": form,
        "cab": associate,
        "cabinet": cabinet,
        "sender": sender,
        "new_cabinet": new_cabinet,
        "cab_id": cab_id,
        "cab_name": cab_name,
    }
    return render(request, "registration/profile.html", context)


@login_required
def ask_for_associate(request):
    """Ask for a partner."""
    if request.method == "POST":
        form = SearchForCabinet(request.POST)
        if form.is_valid():
            askfor = request.POST.get("search_for_cabinet")
            cabinet = Cabinet.objects.filter(name=askfor)
            cabinet = cabinet.first()
            cabass = Associate.objects.filter(cabinet_id=cabinet.id).first()
            obj, _ = RequestAssociate.objects.get_or_create(
                sender_id=request.user.id,
                receiver_id=cabass.user_id,
                cabinet_id=cabass.cabinet_id,
            )
            return HttpResponseRedirect(
                reverse(
                    "nursauth:profile",
                )
            )
    else:
        form = SearchForCabinet()

    return render(
        request,
        "registration/askfor.html",
        {
            "form": form,
            "current_month": now.month,
            "current_year": now.year,
        },
    )


def confirm_associate(request):  # valid_association
    """Confirm associate."""
    sender = None
    associate = None
    lst_associates_id = None
    cab_id = None
    cab_name = None

    associate = Associate.objects.filter(user_id=request.user.id)
    associate = associate.first()

    if associate:
        lst_associates_id = Associate.objects.get_associates(associate.id)
        cab_id = associate.cabinet_id
        cabinet = Cabinet.objects.filter(pk=cab_id).first()
        cab_name = cabinet.name
    valid_form = AssociationValidation(request.POST)
    if request.method == "POST":
        sender_id = request.POST.get("confirm")
        choice = request.POST.get("choice")
        cabinet = Cabinet.objects.filter(pk=cabinet.id).first()

        if sender_id:
            Associate.objects.create(cabinet_id=cabinet.id, user_id=sender_id)

            reqass = RequestAssociate.objects.filter(
                cabinet_id=cabinet.id, sender_id=sender_id
            )
            reqass.delete()
            user = User.objects.filter(pk=sender_id)
            if choice == "associate":
                user.update(is_cabinet_owner=True)
            lst_associates_id = Associate.objects.get_associates(associate.id)

            association_request = RequestAssociate.objects.filter(
                receiver_id=request.user.id
            )
            assreq = association_request.values_list("sender_id", flat=True)
            sender = User.objects.filter(pk__in=[i for i in assreq])

            return HttpResponseRedirect(
                reverse(
                    "nursauth:profile",
                )
            )

    context = {
        "sender": sender,
        "cab_name": cab_name,
        "associates": lst_associates_id,
        "valid_form": valid_form,
    }
    return render(request, "registration/profile.html", context)
