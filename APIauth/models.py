from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser
# Create your models here.

class UserManager(BaseUserManager):

    def create_user(self,name, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            name = name,
            email=(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self,name, email, password):
        user = self.create_user(
            name=name,
            email=email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self,name, email, password):
        user = self.create_user(
            name="admin",
            email=email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    name = models.CharField(max_length=255,)
    email = models.CharField(max_length=255,unique=True, blank=False,)
    password = models.CharField(max_length=512,blank=False,)

    balance = models.IntegerField(default=0, null=False)

    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False) 

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()
