# urls.py in your app folder
from django.urls import path
from data import views
from data.views import notification,calander
from users.views import profile_view
app_name = 'data'
urlpatterns = [
    path('', views.index, name='index'),  # Example URL pattern
    path('dashboard/', views.dashboard, name='dashboard'), 
    path('tasks-tab/', views.tasks_tab, name='tasks_tab'), 
    path('notification/', notification, name='notification'),
    path('calander/', views.calander, name='calander'),
    path('settings/', views.settings, name='settings'),
    path('profile/', profile_view, name='profile'),
]
