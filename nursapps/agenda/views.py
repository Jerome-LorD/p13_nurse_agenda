"""Agenda view module."""
import datetime as dt
import numpy
import calendar

from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from nursapps.agenda.forms import EditEventForm, FormEvent
from nursapps.agenda.models import Event
from nursapps.cabinet.models import Associate
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


def error_404(request, exception):
    """Error 404 view."""
    return render(request, "pages/404.html", status=404)


def index(request):
    """Index view."""
    now = datetime.now()
    return render(
        request,
        "pages/home.html",
        {
            "current_month": now.month,
            "current_year": now.year,
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
                "nurse:main_agenda",
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

    current_month_name = calendar.month_name[month]

    return render(
        request,
        "pages/agenda.html",
        {
            "year": year,
            "month": month,
            "prev_month": prev_month_num,
            "next_month": next_month_num,
            "prev_year": prev_y,
            "next_year": next_y,
            "prev_mnth": prev_month_n,
            "next_mnth": next_month_n,
            "html_calendar": mark_safe(html_cal),
            "user_id": user_id,
            "current_month": now.month,
            "current_year": now.year,
            "current_month_name": current_month_name,
        },
    )


@login_required
def daily_agenda(request, year, month, day):
    """Daily agenda."""
    if not request.user.is_cabinet_owner:
        return HttpResponseRedirect(
            reverse(
                "nursauth:profile",
            )
        )
    now = datetime.now()
    associate = Associate.objects.filter(user_id=request.user.id).first()
    if associate:
        associates = Associate.objects.get_associates(associate.cabinet_id)
        associates = [associate.id for associate in associates]
    else:
        associates = []

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
        date__contains=dt.date(
            year,
            month,
            day,
        ),
        user_id__in=associates,
    )

    booked_hours = [
        appointment.date.strftime("%H:%M")
        for appointment in appointments_per_day
        if request.user.id == appointment.user_id or request.user.id in associates
    ]

    day_name = datetime.strftime(date(year, month, day), "%A")

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
        "booked_hours": booked_hours,
        "uid": user_id,
        "day_name": day_name,
        "current_month": now.month,
        "current_year": now.year,
        "associates": associates,
        "cabinet": associate.cabinet.name,
    }

    return render(request, "pages/daily_agenda_details.html", context)


@login_required
def create_events(request, year, month, day, hour, event_id=None):
    """Create_events."""
    now = datetime.now()

    associate = Associate.objects.filter(user_id=request.user.id).first()
    associates = Associate.objects.get_associates(associate.cabinet_id)
    associates = [associate.id for associate in associates]

    hours = [str(timedelta(hours=hour))[:-3] for hour in numpy.arange(6, 23, 0.25)]
    # adding a zero before single digit:
    hours = [str(datetime.strptime(i, "%H:%M").time())[:5] for i in hours]

    if not is_valid_year_month_day(year, month, day):
        now = datetime.now()
        return HttpResponseRedirect(
            reverse(
                "nurse:new_event",
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

    form = FormEvent(
        request.POST or None,
        user=request.user,
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
    now = datetime.now()
    hour_, minute_ = (int(i) for i in hour.split(":"))
    hour_rdv = str(hour)
    activ = Event.objects.filter(id__iregex=r"^%s$" % event_id)
    event = get_object_or_404(Event, pk=event_id)
    group_event = Event.objects.filter(events_id=event.events_id)

    if request.method == "POST":
        for event in group_event:
            if event.date >= dt.datetime(
                int(year), int(month), int(day), hour_, minute_
            ):
                event.delete()

        return HttpResponseRedirect(
            reverse(
                "nurse:daily_agenda",
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
            "current_month": now.month,
            "current_year": now.year,
            "now": now,
        },
    )


def edit_event(request, year, month, day, hour, event_id):
    """Edit event."""
    now = datetime.now()

    associate = Associate.objects.filter(user_id=request.user.id).first()
    associates = Associate.objects.get_associates(associate.cabinet_id)
    associates = [associate.id for associate in associates]

    hour_rdv = str(hour)
    hours = [str(timedelta(hours=hour))[:-3] for hour in numpy.arange(6, 23, 0.25)]
    # adding a zero before single digit:
    hours = [str(datetime.strptime(i, "%H:%M").time())[:5] for i in hours]

    if not is_valid_year_month_day(year, month, day):
        return HttpResponseRedirect(
            reverse(
                "nurse:edit_event",
                args=[str(now.year), str(now.month), str(now.day), hour, event_id],
            )
        )

    date_of_the_day = datetime(int(year), int(month), int(day)).strftime("%Y-%m-%d")
    event_per_day = Event.objects.filter(
        date__icontains=date_of_the_day, user_id=request.user.id
    ).order_by("name")

    event = get_object_or_404(Event, pk=event_id)
    group_event = Event.objects.filter(events_id=event.events_id)

    day_events = [event.id for event in event_per_day]
    hour_, minute_ = (int(i) for i in hour.split(":"))

    form = EditEventForm(
        request.POST or None,
        user=request.user,
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

    if len(group_event) == 1:
        edit_choice = "thisone"  # To prevent list index out of range with other choices
    edit_choice = request.POST.get("choice_event_edit")

    if request.POST and form.is_valid():
        already = event.update_events(group_event, edit_choice)
        if not already:
            return HttpResponseRedirect(
                reverse(
                    "nurse:daily_agenda",
                    kwargs={"year": year, "month": month, "day": day},
                )
            )
        else:
            # request.session["already_took"] = True
            # request.session["booked_time"] = f"{hour_}:{minute_}"
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
        "pages/event.html",
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
            "current_month": now.month,
            "current_year": now.year,
            "associates": associates,
        },
    )
