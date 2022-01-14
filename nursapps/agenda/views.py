"""Agenda view module."""
import datetime as dt
import numpy
import calendar
import locale

from datetime import datetime, timedelta, date

from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from django.utils.safestring import mark_safe

from nursapps.agenda.forms import EditEventForm, FormEvent
from nursapps.agenda.models import Event
from nursapps.cabinet.models import Associate
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
    get_daily_agenda_hours,
)

now = datetime.now()
format_locale = locale.setlocale(locale.LC_ALL, "fr_FR.utf8")


def error_400(request, exception):
    """Error 400 view."""
    context = {
        "current_month": now.month,
        "current_year": now.year,
    }
    return render(request, "pages/400.html", context, status=400)


def error_404(request, exception):
    """Error 404 view."""
    context = {
        "current_month": now.month,
        "current_year": now.year,
    }
    return render(request, "pages/404.html", context, status=404)


def error_500(request):
    """Error 500 view."""
    context = {
        "current_month": now.month,
        "current_year": now.year,
    }
    return render(request, "pages/500.html", context, status=500)


def index(request):
    """Index home page view."""
    return render(
        request,
        "pages/home.html",
        {"current_month": now.month, "current_year": now.year},
    )


@login_required
def agenda(request, year, month):
    """Show the main agenda view."""
    cal = CalEvent(request.user, year, month)

    if not is_valid_year_month(year, month):
        return HttpResponseRedirect(
            reverse("nurse:main_agenda", args=[str(now.year), str(now.month)])
        )

    html_cal = cal.formatmonth(withyear=True)
    pmb = prev_month_base(year, month, day=1)
    nmb = next_month_base(year, month, day=1)

    return render(
        request,
        "pages/agenda.html",
        {
            "year": year,
            "month": month,
            "prev_month": prev_month_number(pmb),
            "next_month": next_month_number(nmb),
            "prev_year": prev_year(year, month),
            "next_year": next_year(year, month),
            "prev_mnth": prev_month_name(pmb),
            "next_mnth": next_month_name(nmb),
            "html_calendar": mark_safe(html_cal),
            "current_month": now.month,
            "current_year": now.year,
            "current_month_name": calendar.month_name[month],
            "associate_is_replacment": Associate.objects.is_replacment(request.user),
        },
    )


@login_required
def daily_agenda(request, year, month, day):
    """Daily agenda."""
    if request.user.is_cabinet_owner or Associate.objects.is_replacment(request.user):
        associate = Associate.objects.filter(user_id=request.user.id).first()
        if associate:
            associates = Associate.objects.get_associates(associate.cabinet_id)
            associates = [associate.id for associate in associates]
        if is_valid_year_month_day(year, month, day):
            hours = [
                str(timedelta(hours=hour))[:-3] for hour in numpy.arange(6, 23, 0.25)
            ]
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
                if request.user.id == appointment.user_id
                or request.user.id in associates
            ]
        else:
            return HttpResponseRedirect(
                reverse(
                    "nurse:daily_agenda",
                    args=[str(now.year), str(now.month), str(now.day)],
                )
            )
    else:
        return redirect("nursauth:profile")

    context = {
        "year": year,
        "month": month,
        "day": day,
        "hours": [datetime.strptime(i, "%H:%M").time() for i in hours],
        "appointments_per_day": appointments_per_day,
        "prevday": prev_day(year, month, day),
        "nextday": next_day(year, month, day),
        "booked_hours": booked_hours,
        "day_name": datetime.strftime(date(year, month, day), "%A"),
        "current_month": now.month,
        "current_year": now.year,
        "associates": associates,
        "cabinet": associate.cabinet.name,
        "associate_is_replacment": Associate.objects.is_replacment(request.user),
    }

    return render(request, "pages/daily_agenda_details.html", context)


@login_required
def create_events(request, year, month, day, hour, event_id=None):
    """Create_events."""
    associate = Associate.objects.filter(user_id=request.user.id).first()
    associates = Associate.objects.get_associates(associate.cabinet_id)
    associates = [associate.id for associate in associates]

    if not is_valid_year_month_day(year, month, day):
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

    event_per_day = Event.objects.filter(
        date__icontains=f"{year}-{month}-{day}", user_id=request.user.id
    ).order_by("name")

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
        if str(event.date)[11:16] in get_daily_agenda_hours():
            event.create_events(user_id=request.user.id)
            return HttpResponseRedirect(
                reverse(
                    "nurse:daily_agenda",
                    kwargs={"year": year, "month": month, "day": day},
                )
            )
    return render(
        request,
        "pages/event.html",
        {
            "form": form,
            "lst_hours": get_daily_agenda_hours(),
            "year": year,
            "month": month,
            "day": day,
            "hour_rdv": hour,
            "events": [event.id for event in event_per_day],
            "int_event_id": event.id,
            "current_month": now.month,
            "current_year": now.year,
        },
    )


def edit_event(request, year, month, day, hour, event_id):
    """Edit event."""
    associate = Associate.objects.filter(user_id=request.user.id).first()
    associates = Associate.objects.get_associates(associate.cabinet_id)
    associates = [associate.id for associate in associates]
    hours = get_daily_agenda_hours()

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
    cabinet_events = Event.objects.filter(
        user__associate__cabinet_id=associate.cabinet_id
    )
    # This group can be a single event or a recurency event
    group_event = Event.objects.filter(events_id=event.events_id)
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
        form.clean_cares()
        form.clean_day_per_week()
        event.update_events(group_event, edit_choice)
        return HttpResponseRedirect(
            reverse(
                "nurse:daily_agenda",
                kwargs={"year": year, "month": month, "day": day},
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
            "events": [event.id for event in event_per_day],
            "lst_hours": hours,
            "event": event,
            "current_month": now.month,
            "current_year": now.year,
            "associates": associates,
            "cab_events": cabinet_events,
            "event_id_from_cabinet_events": [event.id for event in cabinet_events],
        },
    )


def delete_event(request, year, month, day, hour, event_id):
    """Delete event."""
    hour_, minute_ = (int(i) for i in hour.split(":"))
    event = get_object_or_404(Event, pk=event_id)
    group_event = Event.objects.filter(events_id=event.events_id)

    if request.method == "POST":
        event.delete_event(group_event, year, month, day, hour_, minute_)

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
            "hour_rdv": str(hour),
            "event_id": event_id,
            "year": year,
            "month": month,
            "day": day,
            "current_month": now.month,
            "current_year": now.year,
        },
    )
