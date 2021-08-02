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
        return codeMsg(10200, '账号注册成功')
    else:
        return codeMsg(10406, '激活邮箱不存在')


# 邮箱注册视图类
class EmailRegister(View):
    @method_decorator(emailCheck)
    def post(self, request):
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            return codeMsg(10407, '此邮箱已注册')
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        # Redis 键值
        # email_count:count    email:VCode
        VCode = getRandomNumberStr(6)

        if r.exists(email):
            r.incr(email + '_COUNT', 1)
            if int(r.get(email + '_COUNT')) > 10:
                return codeMsg(10408, '一小时内同一个邮箱只能发10次')
        r.set(email, VCode, ex=settings.REDIS_EXPIRE)
        r.set(email + '_COUNT', 1, ex=settings.REDIS_EXPIRE)
        # 发验证码邮件
        mail.send_mail(
            subject='清问问卷账号注册验证码',
            message='我是根本就不重要',
            html_message="<h4>您的账号验证码为<h1>" + VCode + "</h1></h4>",
            from_email='mail@shaobaitao.cn',
            recipient_list=[email]
        )
        return codeMsg(10201, '邮件发送成功')


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
                'code': 10202,
                'data': {
                    'token': token
                },
                'msg': '登录成功'
            }
            return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")
        else:
            return codeMsg(10409, '用户名或密码不正确')


class EmailForgot(View):
    @method_decorator(emailCheck)
    def post(self, request):
        email = request.POST.get('email')

        if not User.objects.filter(email=email).exists():
            return codeMsg(10410, '此邮箱未注册')

        # 注册db用的0  忘记密码db用的1
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=1)
        VCode = getRandomNumberStr(6)
        if r.exists(email):
            r.incr(email + '_COUNT', 1)
            if int(r.get(email + '_COUNT')) > 10:
                return codeMsg(10408, '一小时内同一个邮箱只能发10次')
        r.set(email, VCode, ex=settings.REDIS_EXPIRE)
        r.set(email + '_COUNT', 1, ex=settings.REDIS_EXPIRE)
        # 发验证码邮件
        mail.send_mail(
            subject='清问问卷账号找回验证码',
            message='我是根本就不重要',
            html_message="<h4>您的账号找回验证码为<h1>" + VCode + "</h1></h4>",
            from_email='mail@shaobaitao.cn',
            recipient_list=[email]
        )
        return codeMsg(10201, '邮件发送成功')


@emailCheck
@passwordCheck
def emailChange(request):
    email = request.POST.get('email')
    VCode = request.POST.get('emailVCode')
    password = request.POST.get('password')

    # 密码找回db为1  email_count:count    email:VCode
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=1)
    if r.exists(email):
        if VCode == r.get(email).decode():
            # 这里email必找到
            user = User.objects.get(email=email)
            user.password = password
            user.save()
        r.delete(email)
        r.delete(email + '_COUNT')
        return codeMsg(10203, '账号密码修改成功')
    else:
        return codeMsg(10406, '激活邮箱不存在')


@tokenCheck
def getInfo(request):
    print(request.payload)
    account = request.payload['username']
    user = User.objects.get(Q(username=account) | Q(email=account) | Q(phone_number=account))
    print(user.id)
    return HttpResponse(request.payload)
