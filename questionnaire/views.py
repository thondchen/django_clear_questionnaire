# Create your views here.
import time
import json
from django.db.models import Q

from questionnaire.decorators.index import *
from questionnaire.models import PROJECT, QUESTION, Q_CHOICE, Q_COMPLETION
from tools.index import *
from user.decorators.user import tokenCheck


def index(request):
    return HttpResponse('ok')


@tokenCheck
@createCheck
def create(request):
    userID = request.payload['id']
    obj = json.loads(request.body.decode())
    title = obj['title']
    desc = obj['desc']

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
    obj = json.loads(request.body)
    count = obj['projectCount']
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


@tokenCheck
@questionPermissionCheck
def deleteProject(request):
    obj = json.loads(request.body)
    id = obj['projectID']

    project = PROJECT.objects.get(id=id)
    project.state = 2
    # 2 是已删除
    project.save()
    return codeMsg(20203, "删除项目成功")


@tokenCheck
@questionPermissionCheck
def createSingleChoice(request):
    obj = json.loads(request.body)

    if len(obj['question']['title']) == 0 or len(obj['question']['options']) < 2:
        return codeMsg(20403, "题目标题不能为空，题目选项大于等于两个，题目选项标题不能为空")

    for i in obj['question']['options']:
        if len(i['title']) == 0:
            return codeMsg(20403, "题目标题不能为空，题目选项大于等于两个，题目选项标题不能为空")

    question = QUESTION.objects.create(
        title=obj['question']['title'],
        required=obj['question']['required'],
        type=1,
        desc=obj['question']['desc'],
        random=obj['question']['random'],
        project_id=obj['projectID'],
    )
    for option in obj['question']['options']:
        Q_CHOICE.objects.create(
            question_id=question.id,
            title=option['title']
        )
    return codeMsg(20204, "单选题创建成功")


@tokenCheck
@questionPermissionCheck
def createMultipleChoice(request):
    obj = json.loads(request.body)
    question = QUESTION.objects.create(
        title=obj['question']['title'],
        required=obj['question']['required'],
        type=2,
        desc=obj['question']['desc'],
        random=obj['question']['random'],
        project_id=obj['projectID'],
    )
    for option in obj['question']['options']:
        Q_CHOICE.objects.create(
            question_id=question.id,
            title=option['title']
        )
    return codeMsg(20205, "多选题创建成功")


@tokenCheck
@questionPermissionCheck
def createCompletion(request):
    obj = json.loads(request.body)
    question = QUESTION.objects.create(
        title=obj['question']['title'],
        required=obj['question']['required'],
        type=3,
        desc=obj['question']['desc'],
        project_id=obj['projectID'],
    )

    Q_COMPLETION.objects.create(
        question_id=question.id,
        regex=obj['question']['regex']
    )
    return codeMsg(20206, "填空题创建成功")
