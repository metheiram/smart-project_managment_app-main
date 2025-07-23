from django.urls import path, include
from django.contrib import admin
from data.views import dashboard,index
from django.contrib.auth import views as auth_views
from django.contrib import admin
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('users/', include('users.urls')),
     path('data/', include('data.urls')),
    path('', dashboard, name='home'),
    path('', include('project.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='project/login.html'), name='login'),
]