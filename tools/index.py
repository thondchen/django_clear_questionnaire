import json

from django.http import HttpResponse


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
