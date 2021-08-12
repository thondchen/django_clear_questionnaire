import json
import redis

from django.core import mail
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import View

from tools.index import getRandomNumberStr
from user.decorators.user import *
from user.models import USER, USER_INFO, USER_LOGIN


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
            # 注册操作
            user = USER.objects.create(email=email, password=password, active=True)
            user.username = 'qw_' + str(user.id)
            user.save()
            USER_INFO.objects.create(
                user=user,
                nickname=user.username,
            )

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
        if USER.objects.filter(email=email).exists():
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
        account = request.POST.get('username')
        password = request.POST.get('password')

        # 登录需要对两张表进行操作 UserInfo UserLogin
        # 主要更新UserInfo中last_login和增加UserLogin中用户登录记录
        userLogin = USER_LOGIN()
        if USER.objects.filter(username=account, password=password).exists():
            user = USER.objects.get(username=account, password=password)
            userLogin.login_mode = 'username'
        elif USER.objects.filter(email=account, password=password).exists():
            user = USER.objects.get(email=account, password=password)
            userLogin.login_mode = 'email'
        elif USER.objects.filter(phone_number=account, password=password).exists():
            user = USER.objects.get(phone_number=account, password=password)
            userLogin.login_mode = 'phone_number'
        else:
            return codeMsg(10409, '用户名或密码不正确')

        userLogin.user = user
        userLogin.username = user.username
        userLogin.ip = request.META["HTTP_X_FORWARDED_FOR"]
        userLogin.os = request.META['HTTP_USER_AGENT']
        userLogin.save()

        userInfo = USER_INFO.objects.get(user_id=user.id)
        userInfo.save()

        token = generateToken(user.id)
        result = {
            'code': 10202,
            'data': {
                'token': token
            },
            'msg': '登录成功'
        }
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")


class EmailForgot(View):
    """
    邮箱找回密码
    """

    @method_decorator(emailCheck)
    def post(self, request):
        email = request.POST.get('email')

        if not USER.objects.filter(email=email).exists():
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
    """
    邮箱修改用户密码
    """
    email = request.POST.get('email')
    VCode = request.POST.get('emailVCode')
    password = request.POST.get('password')

    # 密码找回db为1  email_count:count    email:VCode
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=1)
    if r.exists(email):
        if VCode == r.get(email).decode():
            # 这里email必找到
            user = USER.objects.get(email=email)
            user.password = password
            user.save()
        r.delete(email)
        r.delete(email + '_COUNT')
        return codeMsg(10203, '账号密码修改成功')
    else:
        return codeMsg(10406, '激活邮箱不存在')


@tokenCheck
def getInfo(request):
    """
    获取用户信息
    """
    id = request.payload['id']
    user = USER.objects.get(id=id)
    userInfo = USER_INFO.objects.get(user_id=user.id)
    avatarUrl = settings.IMAGES_URL + str(userInfo.avatar)
    result = {
        'code': 10204,
        'msg': '用户信息获取成功',
        'data': {
            'user': {
                'username': user.username,
                # 'avatar': 'https://wx1.sinaimg.cn/mw2000/005tKgYGly1grraol7esvj30hs0hsab8.jpg',
                'avatar': avatarUrl,
                'last_login': int(time.mktime(userInfo.last_login.timetuple()))
            }
        }
    }

    return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")


@tokenCheck
@usernameCheck
def changeUsername(request):
    newUsername = request.POST.get('newUsername')
    # qaz123
    # 这里不需要查重邮箱和手机号了，装饰器检查过了
    if USER.objects.filter(username=newUsername).exists():
        return codeMsg(10412, '用户名已被使用')
    print(request.payload)
    user = USER.objects.get(id=request.payload['id'])
    user.username = newUsername
    user.save()
    return codeMsg(10205, '用户名修改成功')


@tokenCheck
def uploadAvatar(request):
    avatar = request.FILES['avatar']
    if avatar.size > 1024 * 1024:
        return codeMsg(10412, '图片不能大于1MB')

    userInfo = USER.objects.get(user=request.payload['id'])
    userInfo.avatar = avatar
    userInfo.save()
    return codeMsg(10206, '图片上传成功')
