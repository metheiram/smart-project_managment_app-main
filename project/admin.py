

# Register your models here.
from django.contrib import admin
from .models import CustomUser, Project, Comment
from django.contrib.auth.admin import UserAdmin

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Project)
admin.site.register(Comment)



