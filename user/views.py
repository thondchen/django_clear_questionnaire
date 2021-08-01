import hmac
import json

import redis
from django.core import mail
from django.db.models import Q
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import View

from tools.index import getRandomNumberStr
from user.decorators.user import *
# Create your views here.
from user.models import User


def index(request):
    return HttpResponse("ok")


# 邮箱验证码激活注册账号 过两个检查装饰器
@emailCheck
@passwordCheck
def emailActivate(request):
    email = request.POST.get('email')
    VCode = request.POST.get('emailVCode')
    password = request.POST.get('password')

    # email_count:count    email:VCode
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
    if r.exists(email):
        if VCode == r.get(email).decode():
            user = User.objects.create(email=email, password=password, active=True)
            user.username = 'qw_' + str(user.id)
            user.save()

        r.delete(email)
        r.delete(email + '_COUNT')
        returnCodeMsg(10003, '账号注册成功')
    else:
        returnCodeMsg(10004, '激活邮箱不存在')


# 邮箱注册视图类
class EmailRegister(View):
    @method_decorator(emailCheck)
    def post(self, request):
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            returnCodeMsg(10003, '此邮箱已注册')
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        # Redis 键值
        # email_count:count    email:VCode
        VCode = getRandomNumberStr(6)

        if r.exists(email):
            r.incr(email + '_COUNT', 1)
            if int(r.get(email + '_COUNT')) > 10:
                returnCodeMsg(10002, '一小时内同一个邮箱只能发10次')
        r.set(email, VCode, ex=settings.REDIS_EXPIRE)
        r.set(email + '_COUNT', 1, ex=settings.REDIS_EXPIRE)
        # 发验证码邮件
        mail.send_mail(
            subject='清问问卷账号验证码',
            message='我是根本就不重要',
            html_message="<h4>您的账号验证码为<h1>" + VCode + "</h1></h4>",
            from_email='mail@shaobaitao.cn',
            recipient_list=[email]
        )
        returnCodeMsg(10200, '邮件发送成功')


class AccountLogin(View):
    @method_decorator(accountCheck)
    @method_decorator(passwordCheck)
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(Q(username=username) | Q(email=username) | Q(phone_number=username),
                               password=password).exists():
            token = generateToken(username)
            result = {
                'code': 11200,
                'data': {
                    'token': token
                },
                'msg': '登录成功'
            }
            return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")
        else:
            returnCodeMsg(11400, '用户名或密码不正确')


class EmailForgot(View):
    @method_decorator(emailCheck)
    def post(self, request):
        email = request.POST.get('email')

        if User.objects.filter(email=email).exists() is not True:
            returnCodeMsg(10007, '此邮箱未注册')
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=1)
        if r.exists(email):
            r.incr(email + '_COUNT', 1)
            if int(r.get(email + '_COUNT')) > 10:
                returnCodeMsg(10002, '一小时内同一个邮箱只能发10次')
        else:
            r.set(email + '_COUNT', 1, ex=settings.REDIS_EXPIRE)

        path = hmac.new(settings.TOKEN_SALT.encode(), str(email + '1').encode(), digestmod='SHA256').hexdigest()
        r.set(path, email, ex=settings.REDIS_EXPIRE)
        activeUrl = settings.FRONT_DEPLOY + "/user/email/change/" + path
        mail.send_mail(
            subject='清问问卷账号密码找回',
            message='我是根本就不重要',
            html_message="<h4>请点击链接进行密码找回<a href='" + activeUrl + "'>" + activeUrl + "</a></h4>",
            from_email='mail@shaobaitao.cn',
            recipient_list=[email]
        )
        returnCodeMsg(10200, '邮件发送成功')
