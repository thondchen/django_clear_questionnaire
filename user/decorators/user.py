import json
import re
import time

import jwt
from django.http import HttpResponse
from django.conf import settings


def emailCheck(f):
    def wrap(request, *args, **kwargs):
        email = request.POST.get('email')
        if re.match(r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$', email) is not None:
            return f(request, *args, **kwargs)
        result = {'code': 10001, 'msg': '邮箱格式验证失败'}
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")

    return wrap


def passwordCheck(f):
    def wrap(request, *args, **kwargs):
        password = request.POST.get('password')
        if re.match(r'^\w{64}$', password) is not None:
            return f(request, *args, **kwargs)
        result = {'code': 10006, 'msg': '密码格式验证失败'}
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")

    return wrap


def accountCheck(f):
    def wrap(request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        if re.match(r'^\w{64}$', password) is not None and re.match(r'^{1,20}$', username) is not None:
            return f(request, *args, **kwargs)

        result = {
            'code': 10005,
            'msg': '密码格式错误'
        }
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")

    return wrap


def generateToken(username):
    dic = {
        'username': username,
        'exp': time.time() + settings.TOKEN_EXPIRE
    }
    token = jwt.encode(dic, settings.TOKEN_SALT, 'HS256')
    return token


def checkToken(f):
    def wrap(request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            result = {'code': 10401, 'msg': '未携带Token'}
            return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")

        # noinspection PyBroadException
        try:
            payload = jwt.decode(token, settings.TOKEN_SALT, 'HS256')
        except Exception as e:
            print(e)
            result = {'code': 10402, 'msg': 'Token解析失败'}
            return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")

        request.payload = payload
        return f(request, *args, **kwargs)

    return wrap
