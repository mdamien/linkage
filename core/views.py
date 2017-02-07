from django.shortcuts import render
from django.http import HttpResponse

from core import templates

def index(request):
    return HttpResponse(templates.index())

def result(request):
    return HttpResponse(templates.result())
