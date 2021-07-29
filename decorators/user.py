import json
import re

from django.http import HttpResponse


def emailCheck(f):
    def wrap(request, *args, **kwargs):
        email = request.POST.get('email')
        password = request.POST.get('password')
        if re.match(r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$', email) is not None \
                and re.match(r'^\w{64}$', password) is not None:
            return f(request, *args, **kwargs)

        result = {
            'code': 10001,
            'msg': '邮箱和密码格式验证失败'
        }
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")

    return wrap
