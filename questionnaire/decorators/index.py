import json

from questionnaire.models import PROJECT
from tools.index import codeMsg
import re


def createCheck(f):
    """
    检查问卷项目格式
    """

    def wrap(request, *args, **kwargs):
        obj = json.loads(request.body)

        title = obj['title']
        desc = obj['desc']

        if re.match(r'^[\s\S]{1,100}$', title):
            if re.match(r'^[\s\S]{1,300}$', desc):
                return f(request, *args, **kwargs)
            return codeMsg(20402, "问卷欢迎语长度为1~300")
        return codeMsg(20401, "问卷标题长度为1~100")

    return wrap


def questionPermissionCheck(f):
    """
    检查是否有问题权限
    """

    def wrap(request, *args, **kwargs):
        id = request.payload['id']
        obj = json.loads(request.body)
        if id == PROJECT.objects.get(id=obj['projectID']).user_id:
            return f(request, *args, **kwargs)
        else:
            return codeMsg(20402, "没有题目权限")

    return wrap
