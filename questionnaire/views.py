# Create your views here.
import time

from django.db.models import Q

from questionnaire.decorators.index import createCheck
from questionnaire.models import PROJECT
from tools.index import *
from user.decorators.user import tokenCheck


def index(request):
    return HttpResponse('ok')


@tokenCheck
@createCheck
def create(request):
    userID = request.payload['id']
    title = request.POST['title']
    desc = request.POST['desc']

    PROJECT.objects.create(
        title=title,
        desc=desc,
        state=0,
        user_id=userID
    )
    return codeMsg(20200, "问卷创建成功")


@tokenCheck
def getProjects(request):
    id = request.payload['id']
    count = int(request.POST['count'])
    multiple = 10
    projects = PROJECT.objects.filter(Q(user=id) and ~Q(state=2))[multiple * (count - 1):multiple * count]
    jsonList = querySetToList(projects)
    for inx, dic in enumerate(jsonList):
        dic['created_time'] = int(time.mktime(projects[inx].created_time.timetuple()))

    return codeMsg(20201, "项目列表获取成功", jsonList)


@tokenCheck
def getProjectsCount(request):
    id = request.payload['id']
    count = PROJECT.objects.filter(Q(user=id) and ~Q(state=2)).count()
    return codeMsg(20202, "项目数量获取成功", count)


@tokenCheck
def deleteProject(request):
    id = int(request.POST['id'])

    project = PROJECT.objects.get(id=id)
    project.state = 2
    # 2 是已删除
    project.save()
    return codeMsg(20202, "删除项目成功")
