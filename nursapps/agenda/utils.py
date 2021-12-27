"""Agenda utils module."""
import datetime as dt
import calendar
from datetime import datetime, timedelta
from calendar import HTMLCalendar
from nursapps.agenda.models import Event
from django.template.defaultfilters import pluralize
from nursapps.agenda.models import Associate


class CalEvent(HTMLCalendar):
    """CalEvent class."""

    def __init__(self, user, year=None, month=None):
        """Init."""
        self.year = year
        self.month = month
        self.user = user

        super().__init__()

    def formatday(self, day, activites):
        """Format day."""
        associate = Associate.objects.filter(user_id=self.user.id).first()
        if associate:
            associates = Associate.objects.get_associates(associate.cabinet_id)
            associates = [associate.id for associate in associates]
        else:
            associates = []

        event = Event.objects.filter(
            date__year=self.year,
            date__month=self.month,
            date__day=day,
            user_id__in=associates,
        )
        total_event_by_id = event.count()

        day_ = datetime.today().strftime("%d")
        month_ = datetime.today().strftime("%m")
        if day != 0 and day != int(day_):
            if total_event_by_id == 0:
                return f"<td><a href='{day}'><span class='date'>{day}</span>  </a></td>"
            else:
                return f"<td><a href='{day}'><span class='date'>{day}</span><span class='nb_rdv'>{total_event_by_id} visite{pluralize(total_event_by_id)}</span></a></td>"
        elif day != 0 and day == int(day_) and self.month == int(month_):
            return (
                f"<td class='date-today'><a href='{day}'><span class='date'>{day}</span><span class='nb_rdv'> {total_event_by_id} visite{pluralize(total_event_by_id)}</span></a></td>"
                if total_event_by_id > 0
                else f"<td class='date-today'><a href='{day}'><span class='date'>{day}</span><span class='nb_rdv'> </span></a></td>"
            )
        elif day != 0 and self.month != int(month_):
            if total_event_by_id == 0:
                return f"<td><span class='date'>{day}</span>  </td>"
            else:
                return f"<td><a href='{day}'><span class='date'>{day}</span><span class='nb_rdv'> {total_event_by_id} visite{pluralize(total_event_by_id)}</span></a></td>"
        else:
            return f"<td class='noday'></td>"

    def formatweek(self, theweek, activites):
        """Format week."""
        week = ""
        for datas, weekday in theweek:
            week += self.formatday(datas, activites)

        return f"<tr> {week} </tr>"

    def formatmonth(self, withyear=True):
        """Format month."""
        activites = Event.objects.filter(date__year=self.year, date__month=self.month)
        cal = f'<table class="table" border="0" cellpadding="0" cellspacing="0"><tr><th class="year" colspan="7"> </th></tr>\n'
        cal += f"{self.formatmonthname(self.year, self.month, withyear=True)}\n"
        cal += f"{self.formatweekheader()}\n"
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f"{self.formatweek(week, activites)}\n"
        return cal


def last_day(year, month):
    """Return the last day number of the month."""
    return calendar.monthrange(year, month)[1]


def is_valid_year_month(year, month):
    """Redirect url to the now.year if date is too late."""
    now = datetime.now()
    return (
        True
        if (int(year) == now.year or int(year) == now.year + 1)
        and int(month) in list(range(1, 13))
        else False
    )


def is_valid_year_month_day(year, month, day):
    """Redirect url to the now.year if date is too late."""
    now = datetime.now()
    print("in range : ", int(month) in list(range(1, 13)))
    return (
        True
        if (int(year) == now.year or int(year) == now.year + 1)
        and (int(month) in list(range(1, 13)))
        and (
            int(day)
            in list(range(1, calendar.monthrange(int(year), int(month))[1] + 1))
            or int(day) > 0
        )
        else False
    )


def prev_month_base(year, month, day=1):
    """Return the previous month name."""
    base = dt.date(year, month, day)
    first = base.replace(day=1)
    return first - dt.timedelta(day)


def next_month_base(year, month, day=1):
    """Return the next month name."""
    base = dt.date(year, month, day)
    last_day_of_the_month = calendar.monthrange(year, month)[1]
    last = base.replace(day=last_day_of_the_month)
    return last + timedelta(day)


def prev_month_name(prev_month_base):
    """Return the previous month name."""
    return calendar.month_name[prev_month_base.month]


def prev_month_number(prev_month_base):
    """Return the previous month number."""
    return prev_month_base.strftime("%m")


def next_month_name(next_month_base):
    """Return the next month name."""
    return calendar.month_name[next_month_base.month]


def next_month_number(next_month_base):
    """Return the next month number."""
    return next_month_base.strftime("%m")


def prev_year(year, month):
    """Return the previous year."""
    return year - 1 if month == 1 else year


def next_year(year, month):
    """Return the next year."""
    return year + 1 if month == 12 else year


def prev_day(year, month, day=1):
    """Return the previous day."""
    base = dt.date(int(year), int(month), day)
    base -= dt.timedelta(days=1)
    return base


def next_day(year, month, day):
    """Return the next day."""
    base = dt.date(year, month, day)
    base += dt.timedelta(days=1)
    return base
