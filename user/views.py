import hmac

import redis
from django.core import mail
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.generic import View

from user.decorators.user import *
# Create your views here.
from user.models import User


def index(request):
    return HttpResponse("ok")


def emailActivate(request, link):
    # print(link)
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
    if r.exists(link):
        email = r.get(link).decode()
        password = r.get(email).decode()

        user = User.objects.create(email=email, password=password, active=True)
        user.username = 'qw_' + str(user.id)
        user.save()

        r.delete(link)
        r.delete(email)
        r.delete(email + '_COUNT')
        result = {'code': 10003, 'msg': '邮件激活成功'}
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")
    else:
        result = {'code': 10004, 'msg': '激活地址不存在'}
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")


class EmailRegister(View):
    @method_decorator(emailCheck)
    def post(self, request):
        email = request.POST.get('email')

        if User.objects.filter(email=email).exists():
            result = {'code': 10003, 'msg': '此邮箱已注册'}
            return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")

        password = request.POST.get('password')
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

        if r.exists(email):
            r.incr(email + '_COUNT', 1)
            if int(r.get(email + '_COUNT')) > 10:
                result = {'code': 10002, 'msg': '一小时内同一个邮箱只能发10次'}
                return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")
        else:
            r.set(email, password, ex=settings.REDIS_EXPIRE)
            r.set(email + '_COUNT', 1, ex=settings.REDIS_EXPIRE)

        path = hmac.new(settings.TOKEN_SALT.encode(), email.encode(), digestmod='SHA256').hexdigest()
        r.set(path, email, ex=settings.REDIS_EXPIRE)
        activeUrl = settings.FRONT_DEPLOY + "/user/email/activate/" + path
        mail.send_mail(
            subject='清问问卷账号激活',
            message='我是根本就不重要',
            html_message="<h4>请点击链接进行激活账号<a href='" + activeUrl + "'>" + activeUrl + "</a></h4>",
            from_email='mail@shaobaitao.cn',
            recipient_list=[email]
        )

        result = {'code': 10200, 'msg': '邮件发送成功'}
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")


class AccountLogin(View):
    @method_decorator(accountCheck)
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(Q(username=username) | Q(email=username) | Q(phone_number=username),
                               password=password).exists():
            print('ok')
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
            result = {'code': 11400, 'msg': '用户名或密码不正确'}
            return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")


@checkToken
def tokenTest(request):
    print(type(request.payload))
    return HttpResponse(request.payload)
