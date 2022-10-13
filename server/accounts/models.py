from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

class Profile(models.Model):
    avatar = models.ImageField(upload_to='avatar_img')
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='profile')