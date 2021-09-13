# Create your views here.
import time

from django.db.models import Q
from user.decorators.user import jsonLoad
from questionnaire.decorators.index import *
from questionnaire.models import PROJECT, QUESTION, Q_CHOICE, Q_COMPLETION
from tools.index import *
from user.decorators.user import tokenCheck
from user.models import USER_INFO


def index(request):
    return HttpResponse('ok')


@jsonLoad
@tokenCheck
@createCheck
def create(request):
    userID = request.payload['id']
    title = request.POST['title']
    desc = request.POST['desc']

    project = PROJECT.objects.create(
        title=title,
        desc=desc,
        state=0,
        user_id=userID
    )
    data = {
        'projectID': project.id
    }
    return codeMsg(20200, "问卷创建成功", data)


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
@questionSerialNumber
def createSingleChoice(request):
    question = QUESTION.objects.create(
        title=request.POST['question']['title'],
        required=request.POST['question']['required'],
        type=1,
        desc=request.POST['question']['desc'],
        random=request.POST['question']['random'],
        project_id=request.POST['projectID'],
        serial_number=request.serialNumber
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
@questionSerialNumber
def createMultipleChoice(request):
    question = QUESTION.objects.create(
        title=request.POST['question']['title'],
        required=request.POST['question']['required'],
        type=2,
        desc=request.POST['question']['desc'],
        random=request.POST['question']['random'],
        project_id=request.POST['projectID'],
        serial_number=request.serialNumber
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
@questionSerialNumber
def createCompletion(request):
    question = QUESTION.objects.create(
        title=request.POST['question']['title'],
        required=request.POST['question']['required'],
        type=3,
        desc=request.POST['question']['desc'],
        project_id=request.POST['projectID'],
        serial_number=request.serialNumber
    )

    Q_COMPLETION.objects.create(
        question_id=question.id,
        regex=request.POST['question']['regex']
    )
    return codeMsg(20206, "填空题创建成功")


@jsonLoad
@tokenCheck
@questionPermissionCheck
def getQuestions(request):
    data = {}
    projectID = request.POST['projectID']
    # projectID = 50

    project = PROJECT.objects.get(id=projectID)
    data['id'] = project.id
    data['creator'] = project.user.username
    data['avatar'] = str(USER_INFO.objects.get(user=project.user).avatar)
    data['title'] = project.title
    data['desc'] = project.desc

    questions = QUESTION.objects.filter(state=1).filter(project=project.id).order_by('serial_number')

    data['questions'] = querySetToList(questions)

    for item in data['questions']:
        # print(data['questions'][item].type)
        # print(item.get('type'), type(item))

        if item.get('type') == 1 or item.get('type') == 2:
            options = Q_CHOICE.objects.filter(question_id=item.get('id'))
            options = querySetToList(options)
            item['options'] = options
        elif item.get('type') == 3:
            regex = Q_COMPLETION.objects.get(question_id=item.get('id'))
            item['regex'] = regex.regex

    return codeMsg(20207, "项目问题获取成功", data)


@jsonLoad
@tokenCheck
@questionPermissionCheck
def deleteQuestion(request):
    print(request.POST['questionID'])
    question = QUESTION.objects.get(id=request.POST['questionID'])
    question.state = 0

    # questions = QUESTION.objects.filter(serial_number__gt=question.serial_number)
    QUESTION.objects.filter(serial_number__gt=question.serial_number).update(serial_number=F('serial_number') - 1)
    question.serial_number = 0
    question.save()
    return codeMsg(20208, "项目问题删除成功")


@jsonLoad
@tokenCheck
@questionPermissionCheck
def moveQuestion(request):
    direction = request.POST['direction']
    projectID = request.POST['projectID']
    questionID = request.POST['questionID']

    question = QUESTION.objects.get(id=questionID)
    if direction == 0:  # up
        if question.serial_number == 1:
            return codeMsg(20209, "该项目问题不能上移")
        question.serial_number -= 1

        QUESTION.objects.filter(project=projectID).filter(serial_number=question.serial_number).update(
            serial_number=F('serial_number') + 1)
        question.save()

    else:  # down
        max = QUESTION.objects.filter(project=projectID).aggregate(Max('serial_number'))['serial_number__max']
        if question.serial_number == max:
            return codeMsg(20209, "该项目问题不能下移")
        question.serial_number += 1

        QUESTION.objects.filter(project=projectID).filter(serial_number=question.serial_number).update(
            serial_number=F('serial_number') - 1)
        question.save()
    return codeMsg(20209, "项目问题移动成功")


@jsonLoad
@tokenCheck
# @questionPermissionCheck
def getQuestion(request):
    questionID = request.POST['questionID']
    question = QUESTION.objects.filter(id=questionID)
    data = querySetToList(question)

    for item in data:
        # print(data['questions'][item].type)
        # print(item.get('type'), type(item))

        if item.get('type') == 1 or item.get('type') == 2:
            options = Q_CHOICE.objects.filter(question_id=item.get('id'))
            options = querySetToList(options)
            item['options'] = options
        elif item.get('type') == 3:
            regex = Q_COMPLETION.objects.get(question_id=item.get('id'))
            item['regex'] = regex.regex

    return codeMsg(20210, "项目单个问题获取成功", data)


@jsonLoad
@tokenCheck
@questionPermissionCheck
@radioCheck
@questionSerialNumber
def editSingleChoice(request):
    print(request.POST)
    questionID = request.POST['question']['id']
    QUESTION.objects.filter(id=questionID).update(
        title=request.POST['question']['title'],
        required=request.POST['question']['required'],
        desc=request.POST['question']['desc'],
        random=request.POST['question']['random'],
    )

    # 这边选项修改比较麻烦
    for option in request.POST['question']['options']:
        print(option)
        Q_CHOICE.objects.filter(id=option['id']).update(
            title=option['title']
        )

    return codeMsg(20204, "单选题编辑成功")


@jsonLoad
@tokenCheck
@questionPermissionCheck
@radioCheck
@questionSerialNumber
def editMultipleChoice(request):
    return None


@jsonLoad
@tokenCheck
@questionPermissionCheck
@completionCheck
@questionSerialNumber
def editCompletion(request):
    return None
