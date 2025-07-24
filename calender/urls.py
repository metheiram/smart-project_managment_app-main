# calendar_app/urls.py
from django.urls import path
from . import views

app_name = 'calender'

urlpatterns = [
    path('calender/', views.calender_view, name='calender'),
    path('create/', views.create_event, name='create_event'),
    path('events/json/', views.get_events_json, name='events_json'),
]
