import os
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_Photo = models.ImageField(upload_to='profiles/')

    def delete(self, *args, **kwargs):
        if self.profile_Photo and os.path.isfile(self.profile_Photo.path):
            os.remove(self.profile_Photo.path)
        super(UserProfile, self).delete(*args, **kwargs)

    def __str__(self):
        return self.user.username

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField(blank=True)  # Made blank=True to allow photo-only messages
    image = models.ImageField(upload_to='message_images/', blank=True, null=True)  # Added image field
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def delete(self, *args, **kwargs):
        # Delete the image file when the message is deleted
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super(Message, self).delete(*args, **kwargs)
    
    def __str__(self):
        message_preview = self.content[:20] if self.content else "[Image]"
        return f"{self.sender.username} to {self.receiver.username}: {message_preview}"

class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, related_name='created_groups', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='joined_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    group_photo = models.ImageField(upload_to='group_photos/', blank=True, null=True)  # Added group photo
    
    def delete(self, *args, **kwargs):
        if self.group_photo and os.path.isfile(self.group_photo.path):
            os.remove(self.group_photo.path)
        super(Group, self).delete(*args, **kwargs)
    
    def __str__(self):
        return self.name

class GroupMessage(models.Model):
    group = models.ForeignKey(Group, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='group_messages', on_delete=models.CASCADE)
    content = models.TextField(blank=True)  # Made blank=True to allow photo-only messages
    image = models.ImageField(upload_to='group_message_images/', blank=True, null=True)  # Added image field
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def delete(self, *args, **kwargs):
        # Delete the image file when the message is deleted
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super(GroupMessage, self).delete(*args, **kwargs)
    
    def __str__(self):
        message_preview = self.content[:20] if self.content else "[Image]"
        return f"{self.sender.username} in {self.group.name}: {message_preview}"