"""Cabinet module."""
from django.views.decorators.vary import vary_on_headers
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from nursapps.cabinet.models import Associate, Cabinet, RequestAssociate
from nursapps.nursauth.models import User
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from nursapps.cabinet.forms import (
    CreateCabinetForm,
    SearchCabinetForm,
    AssociationValidationForm,
    DeclineAssociationForm,
    CancelAssociationForm,
)

from django.http.response import (
    Http404,
    JsonResponse,
)

from datetime import datetime
from django.contrib import messages

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


@login_required
def create_new_cabinet(request):
    """Create new cabinet."""
    now = datetime.now()
    form = CreateCabinetForm(request.POST)
    if request.method == "POST":
        cabinet_name = request.POST.get("cabinet_name")
        if form.is_valid():
            if Cabinet.objects.filter(name=cabinet_name).exists():
                if request.user.is_cabinet_owner:
                    return redirect("nursauth:profile")
                messages.add_message(
                    request, messages.INFO, "Copiez/collez " + cabinet_name
                )
                return redirect("cabinet:askfor")
            else:
                cabinet = Cabinet.objects.create(name=cabinet_name)
                request.user.is_cabinet_owner = True
                request.user.save()
                Associate.objects.create(cabinet=cabinet, user=request.user)

                associate = Associate.objects.get(user=request.user)
                associates = Associate.objects.get_associates(associate.cabinet.id)
                return redirect("nursauth:profile")

        else:
            form = CreateCabinetForm()

    context = {
        "cab_form": form,
        "current_month": now.month,
        "current_year": now.year,
    }
    return render(request, "registration/create_cabinet.html", context)


@login_required
def ask_for_associate(request):
    """Ask for a partner."""
    context = {
        "current_month": now.month,
        "current_year": now.year,
    }
    if request.method == "POST":
        form = SearchCabinetForm(request.POST)
        context["form"] = form
        if form.is_valid():
            cabinet_name = request.POST.get("cabinet_name")
            if Cabinet.objects.filter(name=cabinet_name).exists():
                cabinet = Cabinet.objects.filter(name=cabinet_name)
                cabinet = cabinet.first()

                cabinet_associate = Associate.objects.filter(
                    cabinet_id=cabinet.id
                ).first()
                sender_request, _ = RequestAssociate.objects.get_or_create(
                    sender_id=request.user.id,
                    receiver_id=cabinet_associate.user.id,
                    cabinet_id=cabinet_associate.cabinet.id,
                )
                context["user_send_request_for_association"] = sender_request
                return redirect("nursauth:profile")
            else:
                messages.add_message(
                    request, messages.ERROR, "Une erreur s'est produite."
                )
                return reverse("cabinet:askfor")
    else:
        form = SearchCabinetForm()
        context["form"] = form

    return render(request, "registration/askfor.html", context)


@login_required
def confirm_associate(request):
    """Confirm associate."""
    associate = Associate.objects.get(user_id=request.user.id)

    if associate:
        associates = Associate.objects.get_associates(associate.id)
        cabinet = Cabinet.objects.filter(pk=associate.cabinet_id).first()
        context = {"associates": associates}

    if request.method == "POST":
        valid_form = AssociationValidationForm(request.POST)
        context["valid_form"] = valid_form
        if valid_form.is_valid():
            sender_id = request.POST.get("confirm")
            choice = request.POST.get("choice")
            cabinet = Cabinet.objects.filter(pk=cabinet.id).first()
            if sender_id:
                Associate.objects.create(cabinet_id=cabinet.id, user_id=sender_id)
                request_associate = RequestAssociate.objects.filter(
                    cabinet_id=cabinet.id, sender_id=sender_id
                )
                request_associate.delete()
                user = User.objects.filter(pk=sender_id)
                if choice == "associate":
                    user.update(is_cabinet_owner=True)

                associates = Associate.objects.get_associates(associate.id)
                association_request = RequestAssociate.objects.filter(
                    receiver_id=request.user.id
                )
                association_request = association_request.values_list(
                    "sender_id", flat=True
                )
                sender = User.objects.filter(pk__in=[i for i in association_request])
                if sender:
                    context["sender"] = sender
                return redirect("nursauth:profile")
        else:
            valid_form = AssociationValidationForm()
            context["valid_form"] = valid_form
    return render(request, "registration/profile.html", context)


@login_required
def decline_associate(request):
    """Decline associate."""
    associate = Associate.objects.get(user_id=request.user.id)
    if associate:
        cabinet = Cabinet.objects.filter(pk=associate.cabinet_id).first()
    if request.method == "POST":
        decline_form = DeclineAssociationForm(request.POST)
        association_request = RequestAssociate.objects.filter(
            receiver_id=request.user.id
        )
        if decline_form.is_valid():
            sender_id = request.POST.get("decline")
            request_associate = RequestAssociate.objects.filter(
                cabinet_id=cabinet.id, sender_id=int(sender_id)
            ).delete()

            return redirect("nursauth:profile")

    context = {
        "current_month": now.month,
        "current_year": now.year,
        "decline_form": decline_form,
    }

    return render(request, "registration/profile.html", context)


@login_required
def cancel_associate_demand(request):
    """Cancel associate demand."""
    if request.method == "POST":
        cancel_form = CancelAssociationForm(request.POST)
        if cancel_form.is_valid():
            request_associate = RequestAssociate.objects.filter(
                sender_id=request.user.id
            )
            request_associate.delete()
            return redirect("nursauth:profile")

    context = {
        "current_month": now.month,
        "current_year": now.year,
        "cancel_form": cancel_form,
    }

    return render(request, "registration/profile.html", context)
