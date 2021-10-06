from django.urls.resolvers import URLPattern
from . import views

from django.urls import path

urlpatterns = [
    path('',views.main,name = 'main'),
    path('<str:town>',views.get_weather,name = 'get_weather')
]