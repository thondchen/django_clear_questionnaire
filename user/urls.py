from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('email/activate', views.emailActivate),
    path('email/register', views.EmailRegister.as_view()),
    path('email/forgot', views.EmailForgot.as_view()),
    path('email/change', views.emailChange),
    path('account/login', views.AccountLogin.as_view()),

    path('get/info', views.getInfo),

    path('change/username', views.changeUsername),
    path('upload/avatar', views.uploadAvatar),
]
