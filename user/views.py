import hmac
import json
import redis


from django.conf import settings
from django.core import mail
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import View

from decorators.user import emailCheck


# Create your views here.
from user.models import User


def index(request):
    return HttpResponse("ok")


def emailActive(request, link):
    print(link)
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
    if r.exists(link):
        email = r.get(link)
        password = r.get(email)
        User.objects.create(email=email,password=password,active=True)
        return HttpResponse('ok')
    else:
        return HttpResponse(link)


class EmailRegister(View):
    @method_decorator(emailCheck)
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

        if r.exists(email):
            r.incr(email + '_COUNT', 1)
            if int(r.get(email + '_COUNT')) > 10:
                result = {
                    'code': 10002,
                    'msg': '一小时内同一个邮箱只能发10次'
                }
                return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")
        else:
            r.set(email, password, ex=settings.REDIS_EXPIRE)
            r.set(email + '_COUNT', 1, ex=settings.REDIS_EXPIRE)

        path = hmac.new(settings.MY_SALT.encode(), email.encode(), digestmod='SHA256').hexdigest()
        r.set(path, email, ex=settings.REDIS_EXPIRE)
        activeUrl = settings.EMAIL_DEPLOY + "/user/email/active/" + path
        mail.send_mail(
            subject='清问问卷账号激活',
            message='我是根本就不重要',
            html_message="<h4>请点击链接进行激活账号<a href='" + activeUrl + "'>" + activeUrl + "</a></h4>",
            from_email='mail@shaobaitao.cn',
            recipient_list=[email]
        )

        result = {
            'code': 10200,
            'msg': '邮件发送成功'
        }
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")
