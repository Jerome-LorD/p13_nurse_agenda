from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


# @login_required
def index(request):
    """Index view."""
    return HttpResponse("Bienvenue sur ce site en construction")
    # cal = CustomHTMLCal(int(current_year), int(current_month))
    # return render(request, "pages/home.html", {"cal": cal.formatmonth()})
