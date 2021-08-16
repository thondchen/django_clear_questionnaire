from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from questionnaire.decorators.index import createCheck
from questionnaire.models import PROJECT
from tools.index import codeMsg
from user.decorators.user import tokenCheck


def index(request):
    return HttpResponse('ok')


@tokenCheck
@createCheck
def create(request):
    userID = request.payload['id']
    title = request.POST.get('title')
    desc = request.POST.get('desc')

    PROJECT.objects.create(
        title=title,
        desc=desc,
        state=0,
        user_id=userID
    )
    return codeMsg(20200, "问卷创建成功")
