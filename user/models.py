from django.db import models


# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=11)
    active = models.BooleanField(default=False)


class UserInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    nickname = models.CharField(max_length=100)
    registration_time = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    birthday = models.DateField()
    gender = models.CharField(max_length=10)
    avatar = models.ImageField()
