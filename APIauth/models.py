from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    name = models.CharField(max_length=255,blank=False,)
    email = models.CharField(max_length=255,unique=True, blank=False,)
    password = models.CharField(max_length=512,blank=False,)

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
