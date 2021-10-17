from main.script.info_parser import TownError
from django.http.response import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from main.script.runscript import run
from datetime import date, timedelta
from main.script.configure import DAYS,MONTHS
from json import dumps
# Create your views here.

def main(request):
    return render(request,'main/index.html')

def get_weather(request,town):
    town = town.lower()
    today_date = date.today()
    if request.method == 'POST':
        town = request.POST['town']
        return HttpResponseRedirect(reverse('get_weather',args = (town,)))
    try:
        info = run(town)
    except TownError:
        return render(request,'main/http404.html')
    return render(request,'main/get_weather.html',{'info':info,
    'current_date':today_date,
    'dates_for_header':dumps(["{} {}".format((today_date + timedelta(days = i)).day,MONTHS[(today_date + timedelta(days = i)).month -1]) for i in range(6)]),
    'town':town.capitalize(),
    'days':dumps([day.capitalize() for day in DAYS]),
    'month':MONTHS[today_date.month - 1],
    'JSONDATA':dumps(info)})
