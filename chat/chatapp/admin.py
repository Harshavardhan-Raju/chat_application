from django.contrib import admin
from .models import UserProfile, Message

admin.site.register(UserProfile)
admin.site.register(Message)