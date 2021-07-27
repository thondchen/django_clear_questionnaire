import csv
import time

from django.shortcuts import render

from django.http import HttpResponse

from django.core import mail
from django.utils.http import urlquote

from django.views.decorators.cache import cache_page


# Create your views here.
def index(request):
    return HttpResponse("ok")
