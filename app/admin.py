# app/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


admin.site.register(Calendar)
admin.site.register(Note)
admin.site.register(CustomUser)
admin.site.register(Vegetable)
admin.site.register(Prediction)