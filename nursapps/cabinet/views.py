"""Cabinet module."""
from datetime import datetime

from django.views.decorators.vary import vary_on_headers
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.contrib import messages

from nursapps.cabinet.models import Associate, Cabinet, RequestAssociate
from nursapps.nursauth.models import User
from nursapps.cabinet.forms import (
    CreateCabinetForm,
    SearchCabinetForm,
    AssociationValidationForm,
    DeclineAssociationForm,
    CancelAssociationForm,
)


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
    form = CreateCabinetForm(request.POST)
    if request.method == "POST":
        cabinet_name = request.POST.get("cabinet_name")
        if form.is_valid():
            form.clean_cabinet_name()
            if Cabinet.objects.filter(name=cabinet_name).exists():
                if request.user.is_cabinet_owner:
                    return redirect("nursauth:profile")
                messages.add_message(
                    request, messages.INFO, f"Copiez/collez : {cabinet_name}"
                )
                return redirect("cabinet:askfor")
            else:
                if cabinet_name != "":
                    cabinet = Cabinet.objects.create(name=cabinet_name)
                    request.user.is_cabinet_owner = True
                    request.user.save()
                    Associate.objects.create(cabinet=cabinet, user=request.user)

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
    """Ask for a partner.

    To join a cabinet, the user must send a request.
    """
    context = {}
    if request.method == "POST":
        form = SearchCabinetForm(request.POST)
        if form.is_valid():
            form.clean_cabinet_name()
            cabinet_name = request.POST.get("cabinet_name")
            user_demand = RequestAssociate.objects.filter(sender_id=request.user.id)
            if (
                Cabinet.objects.filter(name=cabinet_name).exists()
                and not request.user.is_cabinet_owner
                and not user_demand
            ):
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
            elif Cabinet.objects.filter(name=cabinet_name).exists() and (
                request.user.is_cabinet_owner or user_demand
            ):
                messages.add_message(
                    request,
                    messages.ERROR,
                    ("Vous ne pouvez pas être affilié à plusieurs cabinets."),
                )
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    ("Attention, ce nom de cabinet n'existe pas :/"),
                )
            return redirect("cabinet:askfor")
    else:
        form = SearchCabinetForm()
    context = {
        "current_month": now.month,
        "current_year": now.year,
        "form": form,
    }
    return render(request, "registration/askfor.html", context)


@login_required
def confirm_associate(request):
    """Confirm associate."""
    associate = Associate.objects.get(user_id=request.user.id)
    if associate:
        associates = Associate.objects.get_associates(associate.id)
        cabinet = Cabinet.objects.filter(pk=associate.cabinet_id).first()

    if request.method == "POST":
        valid_form = AssociationValidationForm(request.POST)
        if valid_form.is_valid():
            sender_id = request.POST.get("confirm")
            choice = request.POST.get("choice")
            cabinet = Cabinet.objects.filter(pk=cabinet.id).first()
            if sender_id:
                Associate.objects.create(cabinet_id=cabinet.id, user_id=sender_id)
                RequestAssociate.objects.filter(
                    cabinet_id=cabinet.id, sender_id=sender_id
                ).delete()
                user = User.objects.filter(pk=sender_id)
                if choice == "associate" or "collaborator":
                    user.update(is_cabinet_owner=True)
                return redirect("nursauth:profile")
    else:
        valid_form = AssociationValidationForm()

    context = {"valid_form": valid_form, "associates": associates}
    return render(request, "registration/profile.html", context)


@login_required
def decline_associate(request):
    """Decline associate.

    The owner of the cabinet can refuse the association request.
    """
    associate = Associate.objects.get(user_id=request.user.id)
    if associate:
        cabinet = Cabinet.objects.filter(pk=associate.cabinet_id).first()
    if request.method == "POST":
        decline_form = DeclineAssociationForm(request.POST)
        if decline_form.is_valid():
            sender_id = request.POST.get("decline")
            RequestAssociate.objects.filter(
                cabinet_id=cabinet.id, sender_id=int(sender_id)
            ).delete()

            return redirect("nursauth:profile")
    else:
        decline_form = DeclineAssociationForm()

    context = {
        "current_month": now.month,
        "current_year": now.year,
        "decline_form": decline_form,
    }

    return render(request, "registration/profile.html", context)


@login_required
def cancel_associate_demand(request):
    """Cancel associate demand.

    The user can cancel their own demand.
    """
    if request.method == "POST":
        cancel_form = CancelAssociationForm(request.POST)
        if cancel_form.is_valid():
            request_associate = RequestAssociate.objects.filter(
                sender_id=request.user.id
            )
            request_associate.delete()
            return redirect("nursauth:profile")
    else:
        cancel_form = CancelAssociationForm()

    context = {
        "current_month": now.month,
        "current_year": now.year,
        "cancel_form": cancel_form,
    }

    return render(request, "registration/profile.html", context)
