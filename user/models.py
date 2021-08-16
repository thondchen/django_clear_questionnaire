from django.db import models


# Create your models here.

class USER(models.Model):
    username = models.CharField(max_length=60)
    password = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=60)
    state = models.IntegerField()
    status = models.IntegerField()


class USER_INFO(models.Model):
    user = models.ForeignKey(USER, on_delete=models.DO_NOTHING)
    registration_time = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    gender = models.IntegerField(null=True)
    avatar = models.ImageField(upload_to='avatar')
    nickname = models.CharField(max_length=100)
    birthday = models.DateField(default='1900-01-01')


class USER_LOGIN(models.Model):
    user = models.ForeignKey(USER, on_delete=models.DO_NOTHING)
    username = models.CharField(max_length=100)
    login_time = models.DateTimeField(auto_now=True)
    ip = models.GenericIPAddressField()
    os = models.CharField(max_length=200)
    login_mode = models.CharField(max_length=100, default='')
