from tools.index import codeMsg
import re


def createCheck(f):
    """
    检查邮箱格式
    """

    def wrap(request, *args, **kwargs):
        title = request.POST.get('title')
        desc = request.POST.get('desc')

        if re.match(r'^[\s\S]{1,100}$', title):
            if re.match(r'^[\s\S]{1,300}$', desc):
                return f(request, *args, **kwargs)
            return codeMsg(20402, "问卷欢迎语长度为1~300")
        return codeMsg(20401, "问卷标题长度为1~100")

    return wrap
