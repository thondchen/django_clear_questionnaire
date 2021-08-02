import json

from django.http import HttpResponse

"""
10401, '邮箱格式验证失败'
10402, '密码格式验证失败'
10403, '账号格式错误'
10404, '未携带Token'
10405, 'Token解析失败'

10200, '账号注册成功'
10406, '激活邮箱不存在'
10407, '此邮箱已注册'
10408, '一小时内同一个邮箱只能发10次'
10201, '邮件发送成功'
10202, '登录成功' data
10409, '用户名或密码不正确'
10410, '此邮箱未注册'
10203, '账号密码修改成功'
"""


def getRandomNumberStr(bit):
    """
    生成多少位的随机验证码
    """
    import random
    str = ''
    for i in range(bit):
        ch = chr(random.randrange(ord('0'), ord('9') + 1))
        str += ch
    return str


def codeMsg(code: int, msg: str):
    """
    返回携带状态码和信息的HttpResponse
    HttpResponse code and message
    """
    dic = {'code': code, 'msg': msg}
    return HttpResponse(json.dumps(dic, ensure_ascii=False), content_type="application/json")
