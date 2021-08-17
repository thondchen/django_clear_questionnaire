import json

from django.db.models import QuerySet
from django.forms import model_to_dict
from django.http import HttpResponse


def getRandomNumberStr(bit: int) -> str:
    """生成多少位的随机验证码"""
    import random
    str = ''
    for i in range(bit):
        ch = chr(random.randrange(ord('0'), ord('9') + 1))
        str += ch
    return str


def codeMsg(code: int, msg: str, *data) -> HttpResponse:
    """
    返回携带状态码和信息的HttpResponse
    HttpResponse code and message
    """
    if len(data) == 0:
        dic = {'code': code, 'msg': msg}
        return HttpResponse(json.dumps(dic, ensure_ascii=False), content_type="application/json")
    else:
        dic = {'code': code, 'msg': msg, 'data': data[0]}
        return HttpResponse(json.dumps(dic, ensure_ascii=False), content_type="application/json")


def querySetToList(qs: QuerySet) -> list:
    """把ORM查询出来的querySet转换成list"""
    jsonList = []
    for i in qs:
        jsonDict = model_to_dict(i)
        jsonList.append(jsonDict)
    return jsonList
