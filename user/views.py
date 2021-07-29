import json
import uuid
import redis
import hmac
from django.core import mail
from django.http import HttpResponse
from django.utils.decorators import method_decorator

from django.views.generic import View
from decorators.user import emailCheck
from django.conf import settings


# Create your views here.


def index(request):
    return HttpResponse("ok")


def emailActive(request, link):
    print(link)
    return HttpResponse(link)


class EmailRegister(View):
    @method_decorator(emailCheck)
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

        if r.exists(email):
            r.incr(email + 'COUNT', 1)
            if int(r.get(email + 'COUNT')) > 10:
                result = {
                    'code': 10002,
                    'msg': '一小时内同一个邮箱只能发10次'
                }
                return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")
        else:
            r.set(email, password, ex=settings.REDIS_EXPIRE)
            r.set(email + '_COUNT', 1, ex=settings.REDIS_EXPIRE)
        # mail.send_mail(subject='测试邮箱发送', message='<h1>hello</h1>', from_email='mail@shaobaitao.cn',
        #                recipient_list=['ethan_shao@qq.com'])
        print(email+'邮箱激活')
        # path = uuid.uuid5(uuid.NAMESPACE_DNS, settings.MY_SALT)
        path = hmac.new(settings.MY_SALT.encode(), email.encode(), digestmod='SHA256').hexdigest()
        r.set(email + '_SALT', path, ex=settings.REDIS_EXPIRE)
        mail.send_mail(
            subject='清问问卷账号激活',
            message='我是根本就不重要',
            html_message="<h4>请点击链接进行激活账号"+settings.EMAIL_DEPLOY+"email/active/"+path+"</h4>",
            from_email='mail@shaobaitao.cn',
            recipient_list=[email]
        )

        result = {
            'code': 10200,
            'msg': '邮件发送成功'
        }
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")

# def emailRegister(request):
