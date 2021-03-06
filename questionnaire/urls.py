from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create', views.create),
    path('deleteProject', views.deleteProject),

    path('getProjects', views.getProjects),
    path('getProjectsCount', views.getProjectsCount),

    path('getQuestion', views.getQuestion),
    path('getQuestions', views.getQuestions),

    path('deleteQuestion', views.deleteQuestion),
    path('moveQuestion', views.moveQuestion),

    path('createSingleChoice', views.createSingleChoice),
    path('createMultipleChoice', views.createMultipleChoice),
    path('createCompletion', views.createCompletion),

    path('editSingleChoice', views.editSingleChoice),
    path('editMultipleChoice', views.editMultipleChoice),
    path('editCompletion', views.editCompletion),

]
