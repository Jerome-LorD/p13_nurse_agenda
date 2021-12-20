"""Agenda view module."""
import datetime as dt
import locale
import numpy

from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from nursapps.agenda.forms import formEvent
from nursapps.agenda.models import Event
from datetime import datetime, timedelta, date
from django.utils.safestring import mark_safe

from nursapps.agenda.utils import (
    CalEvent,
    is_valid_year_month,
    is_valid_year_month,
    is_valid_year_month_day,
    prev_month_base,
    next_month_base,
    prev_month_name,
    next_month_name,
    prev_month_number,
    next_month_number,
    next_day,
    prev_day,
    next_year,
    prev_year,
)


def trigger_error(request):
    """Sentry test."""
    division_by_zero = 1 / 0


@login_required
def index(request):
    """Index view."""
    now = datetime.now()
    # breakpoint()
    cal = CalEvent(request.user, now.year, now.month)
    html_cal = cal.formatmonth(withyear=True)
    return render(
        request,
        "pages/home.html",
        {
            "current_month": now.month,
            "current_year": now.year,
            "html_calendar": mark_safe(html_cal),
        },
    )


@login_required
def agenda(request, year, month):
    """Show the main agenda view."""
    now = datetime.now()
    cal = CalEvent(request.user, year, month)

    if not is_valid_year_month(year, month):
        return HttpResponseRedirect(
            reverse(
                "agenda:main_agenda",
                args=[str(now.year), str(now.month)],
            )
        )

    html_cal = cal.formatmonth(withyear=True)
    user_id = request.user.id
    user_date_joined = request.user.date_joined
    user_date_joined = datetime.strptime(str(user_date_joined)[:10], "%Y-%m-%d").date()

    pmb = prev_month_base(year, month, day=1)
    nmb = next_month_base(year, month, day=1)
    prev_month_n = prev_month_name(pmb)
    next_month_n = next_month_name(nmb)
    prev_month_num = prev_month_number(pmb)
    next_month_num = next_month_number(nmb)
    prev_y = prev_year(year, month)
    next_y = next_year(year, month)

    return render(
        request,
        "pages/agenda.html",
        {
            "year": year,
            "month": month,
            "prec_mois": prev_month_num,
            "suiv_mois": next_month_num,
            "prec_an": prev_y,
            "suiv_an": next_y,
            "prev": prev_month_n,
            "nextmth": next_month_n,
            "html_calendar": mark_safe(html_cal),
            "user_id": user_id,
            "current_month": now.month,
            "current_year": now.year,
        },
    )


@login_required(redirect_field_name="home")
def home(request):
    """Home view."""
    year = datetime.today().year
    month = datetime.today().month
    day = datetime.today().day
    ndm = datetime.strftime(date(year, month, day), "%B")
    nomdujour = datetime.strftime(date(year, month, day), "%A")
    cabinet = request.user.groups.values_list("name", flat=True).first()

    return render(
        request,
        "pages/home.html",
        {
            "year": year,
            "month": month,
            "day": day,
            "cabinet": cabinet,
            "nomdujour": nomdujour,
            "ndm": ndm,
        },
    )


@login_required
def daily_agenda(request, year, month, day):
    """Agenda jour."""
    now = datetime.now()
    event = Event.objects.filter(user_id=request.user.id).first()

    if not is_valid_year_month_day(year, month, day):
        return HttpResponseRedirect(
            reverse(
                "nurse:daily_agenda",
                args=[str(now.year), str(now.month), str(now.day)],
            )
        )

    hours = [str(timedelta(hours=hour))[:-3] for hour in numpy.arange(6, 23, 0.25)]
    # adding a zero before single digit:
    hours = [datetime.strptime(i, "%H:%M").time() for i in hours]

    user_id = request.user.id
    appointments_per_day = Event.objects.filter(
        date__contains=dt.date(year, month, day)
    )

    lapj = [
        appointment.date.strftime("%H:%M")
        for appointment in appointments_per_day
        if request.user.id == appointment.user_id
    ]

    nb_rdv_par_jour = Event.objects.filter(
        date__contains=dt.date(year, month, day)
    ).count()

    nom_du_jour = datetime.strftime(date(year, month, day), "%A")
    heure_courante = datetime.strftime(datetime.now(), "%H:%M")
    hcourante = datetime.strftime(datetime.now(), "%H%M")[:-1]
    heure_unik = datetime.strftime(datetime.now(), "%H")

    nextday = next_day(year, month, day)
    prevday = prev_day(year, month, day)

    context = {
        "year": year,
        "month": month,
        "day": day,
        "hours": hours,
        "appointments_per_day": appointments_per_day,
        "prevday": prevday,
        "nextday": nextday,
        "lapj": lapj,
        "uid": user_id,
        "nom_du_jour": nom_du_jour,
        "hcour": heure_courante,
        "hunik": heure_unik,
        "hcou": hcourante,
        "nb_rdv": nb_rdv_par_jour,
        "current_month": now.month,
        "current_year": now.year,
    }

    return render(request, "pages/daily_agenda_details.html", context)


format_locale = locale.setlocale(locale.LC_ALL, "French_France.1252")


@login_required
def create_events(request, year, month, day, hour, event_id=None):
    """Create_events."""
    now = datetime.now()
    print("!!!!!!!!!!!!!!!!!!!!!!!DANS CREATE EVENT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    hours = [str(timedelta(hours=hour))[:-3] for hour in numpy.arange(6, 23, 0.25)]
    # adding a zero before single digit:
    hours = [str(datetime.strptime(i, "%H:%M").time())[:5] for i in hours]

    # if not is_valid_date(int(year), int(month), int(day), hour):

    if not is_valid_year_month_day(year, month, day):
        now = datetime.now()
        return HttpResponseRedirect(
            reverse(
                "agenda:agenda_neo_rdv",
                kwargs={
                    "year": now.year,
                    "month": now.month,
                    "day": now.day,
                    "hour": hour,
                },
            )
        )

    date_of_the_day = datetime(int(year), int(month), int(day)).strftime("%Y-%m-%d")

    event_per_day = Event.objects.filter(
        date__icontains=date_of_the_day, user_id=request.user.id
    ).order_by("name")

    day_events = [event.id for event in event_per_day]
    warn = False
    if event_id:
        event = get_object_or_404(Event, pk=event_id)
    else:
        event = Event()

    hour_, minute_ = (int(i) for i in hour.split(":"))

    form = formEvent(
        request.POST or None,
        instance=event,
        initial={
            "cares": event.cares.split(", "),
            "date": event.date.strftime("%Y-%m-%dT%H:%M")
            if event.date
            else dt.datetime(int(year), int(month), int(day), hour_, minute_).strftime(
                "%Y-%m-%dT%H:%M"
            ),
        },
    )

    if request.POST and form.is_valid():
        form.clean_cares()
        form.clean_day_per_week()

        if str(event.date)[11:16] in hours:
            event.create_events(user_id=request.user.id)

            return HttpResponseRedirect(
                reverse(
                    "nurse:daily_agenda",
                    kwargs={"year": year, "month": month, "day": day},
                )
            )
        else:
            warn = True
            return render(
                request,
                "pages/event.html",
                {"warn": warn, "year": year, "month": month},
            )

    return render(
        request,
        "pages/event.html",
        {
            "form": form,
            "event_id": event_id,
            "lst_hours": hours,
            "warn": warn,
            "year": year,
            "month": month,
            "day": day,
            "hour_rdv": hour,
            "events": day_events,
            "int_event_id": event.id,
            "current_month": now.month,
            "current_year": now.year,
        },
    )


def delete_event(request, year, month, day, hour, event_id):
    """Delete event."""
    hour_, minute_ = (int(i) for i in hour.split(":"))
    hour_rdv = str(hour)
    activ = Event.objects.filter(id__iregex=r"^%s$" % event_id)
    event = get_object_or_404(Event, pk=event_id)
    group_event = Event.objects.filter(group_id=event.group_id)

    if request.method == "POST":
        # TODO: add possibility to delete the event_id only. Not the entire group.
        # if del_only_a_day: boolean from checkbox.
        # If the checkbox is checked, del_only_a_day = True
        # if del_only_a_day:
        #     event.delete()
        for event in group_event:
            # TODO: delete only the events of the day during consultation with the
            # events planned after and which are part of the group_event.
            # Do not delete events before this date!
            if event.date >= dt.datetime(
                int(year), int(month), int(day), hour_, minute_
            ):
                event.delete()

        return HttpResponseRedirect(
            reverse(
                "agenda:agendadujour",
                kwargs={"year": year, "month": month, "day": day},
            )
        )
    return render(
        request,
        "pages/del_event.html",
        {
            "hour_rdv": hour_rdv,
            "event_id": event_id,
            "year": year,
            "month": month,
            "day": day,
            "activ": activ,
        },
    )


def edit_event(request, year, month, day, hour, event_id):
    """Edit event."""
    # TODO:
    hour_rdv = str(hour)
    hours = [str(timedelta(hours=hour))[:-3] for hour in numpy.arange(6, 23, 0.25)]
    # adding a zero before single digit:
    hours = [str(datetime.strptime(i, "%H:%M").time())[:5] for i in hours]

    date_of_the_day = datetime(int(year), int(month), int(day)).strftime("%Y-%m-%d")
    event_per_day = Event.objects.filter(
        date__icontains=date_of_the_day, user_id=request.user.id
    ).order_by("name")

    event = get_object_or_404(Event, pk=event_id)
    group_event = Event.objects.filter(group_id=event.group_id)
    # form = formEvent()

    day_events = [event.id for event in event_per_day]
    # breakpoint()
    hour_, minute_ = (int(i) for i in hour.split(":"))

    # day_per_week = event.day_per_week.split(", ")
    # breakpoint()

    form = formEvent(
        request.POST or None,
        instance=event,
        initial={
            "day_per_week": event.day_per_week.split(", ")
            if event.day_per_week
            else None,
            "cares": event.cares.split(", "),
            "date": event.date.strftime("%Y-%m-%dT%H:%M")
            if event.date
            else dt.datetime(int(year), int(month), int(day), hour_, minute_).strftime(
                "%Y-%m-%dT%H:%M"
            ),
        },
    )
    # editable_forms = {
    #     "formdate": form["date"].value(),
    #     "formname": form["name"].value(),
    #     "formcares": form["cares"].value(),
    # }
    if request.POST and form.is_valid():
        already = event.update_events(group_event)
        if not already:
            return HttpResponseRedirect(
                reverse(
                    "nurse:daily_agenda",
                    kwargs={"year": year, "month": month, "day": day},
                )
            )
        else:
            request.session["already_took"] = True
            request.session["booked_time"] = f"{hour_}:{minute_}"
            return HttpResponseRedirect(
                reverse(
                    "nurse:edit_event",
                    kwargs={
                        "year": year,
                        "month": month,
                        "day": day,
                        "hour": hour,
                        "event_id": event_id,
                    },
                )
            )
    return render(
        request,
        "trocnco/event.html",
        {
            "form": form,
            "hour_rdv": event.date.strftime("%H:%M"),
            "event_id": event_id,
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "int_event_id": int(event.id),
            "events": day_events,
            "lst_hours": hours,
            "event": event,
            # "selected_date": editable_forms["formdate"][-5:],
        },
    )
