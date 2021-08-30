# Create your views here.
import time

from django.db.models import Q
from user.decorators.user import jsonLoad
from questionnaire.decorators.index import *
from questionnaire.models import PROJECT, QUESTION, Q_CHOICE, Q_COMPLETION
from tools.index import *
from user.decorators.user import tokenCheck


def index(request):
    return HttpResponse('ok')


@jsonLoad
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


@jsonLoad
@tokenCheck
def getProjects(request):
    id = request.payload['id']
    count = request.POST['projectCount']
    multiple = 10
    print(id)
    projects = PROJECT.objects.filter(Q(user=id) & ~Q(state=2)).order_by('-id')[multiple * (count - 1):multiple * count]
    jsonList = querySetToList(projects)
    for inx, dic in enumerate(jsonList):
        dic['created_time'] = int(time.mktime(projects[inx].created_time.timetuple()))

    return codeMsg(20201, "项目列表获取成功", jsonList)


@tokenCheck
def getProjectsCount(request):
    id = request.payload['id']
    count = PROJECT.objects.filter(Q(user=id) & ~Q(state=2)).count()
    return codeMsg(20202, "项目数量获取成功", count)


@jsonLoad
@tokenCheck
@questionPermissionCheck
def deleteProject(request):
    id = request.POST['projectID']

    project = PROJECT.objects.get(id=id)
    project.state = 2
    # 2 是已删除
    project.save()
    return codeMsg(20203, "删除项目成功")


@jsonLoad
@tokenCheck
@questionPermissionCheck
@radioCheck
def createSingleChoice(request):
    question = QUESTION.objects.create(
        title=request.POST['question']['title'],
        required=request.POST['question']['required'],
        type=1,
        desc=request.POST['question']['desc'],
        random=request.POST['question']['random'],
        project_id=request.POST['projectID'],
    )
    for option in request.POST['question']['options']:
        Q_CHOICE.objects.create(
            question_id=question.id,
            title=option['title']
        )
    return codeMsg(20204, "单选题创建成功")


@jsonLoad
@tokenCheck
@questionPermissionCheck
@radioCheck
def createMultipleChoice(request):
    question = QUESTION.objects.create(
        title=request.POST['question']['title'],
        required=request.POST['question']['required'],
        type=2,
        desc=request.POST['question']['desc'],
        random=request.POST['question']['random'],
        project_id=request.POST['projectID'],
    )
    for option in request.POST['question']['options']:
        Q_CHOICE.objects.create(
            question_id=question.id,
            title=option['title']
        )
    return codeMsg(20205, "多选题创建成功")


@jsonLoad
@tokenCheck
@questionPermissionCheck
@completionCheck
def createCompletion(request):
    question = QUESTION.objects.create(
        title=request.POST['question']['title'],
        required=request.POST['question']['required'],
        type=3,
        desc=request.POST['question']['desc'],
        project_id=request.POST['projectID'],
    )

    Q_COMPLETION.objects.create(
        question_id=question.id,
        regex=request.POST['question']['regex']
    )
    return codeMsg(20206, "填空题创建成功")
