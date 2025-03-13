from django.contrib.auth.models import AbstractUser
from django.db import models

def avatar_upload_path(instance, filename):
    return f'avatars/{instance.username}/{filename}'

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('author', 'Author'),
        ('reader', 'Reader'),
    )
    
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='reader')

    def __str__(self):
        return self.username
    
    @property
    def is_editor_or_admin(self):
        return self.role in ['editor', 'admin'] or self.is_staff