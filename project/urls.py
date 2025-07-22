from django.urls import path,include
from . import views
from django.contrib import admin
app_name = 'project'

urlpatterns = [
     path('admin/', admin.site.urls),
     path('data/', include('data.urls')), 
    #path('data/', views.dashboard, name='dashboard'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
     path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('register/', views.register, name='register'),
     path('project-tab/', views.project_tab, name='project_tab'),
     path('projects/create/', views.project_create, name='project_create'),
]
