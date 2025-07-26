from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/setup/', views.profile_setup_view, name='profile_setup'),
    path('settings/', views.settings_view, name='settings'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)