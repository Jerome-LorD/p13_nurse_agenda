from django.http.response import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def index(request):
    """Index view."""
    # cal = CustomHTMLCal(int(current_year), int(current_month))
    # return render(request, "pages/home.html", {"cal": cal.formatmonth()})
    return HttpResponse("Page d'accueil")


# @login_required
def home(request, year, month):
    """Home calendar view."""
    #     cal = CustomHTMLCal(year, month)
    #     return render(request, "pages/home.html", {"cal": cal.formatmonth()})
    return HttpResponse("Page d'accueil")
