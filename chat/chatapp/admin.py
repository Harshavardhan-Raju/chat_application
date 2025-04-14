from django.contrib import admin
from .models import UserProfile, Message,Group,GroupMessage

admin.site.register(UserProfile)
admin.site.register(Message)
admin.site.register(Group)
admin.site.register(GroupMessage)