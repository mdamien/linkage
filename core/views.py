import csv
from io import TextIOWrapper

from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from core import templates, models

def index(request):
    if request.POST and request.FILES:
        links = TextIOWrapper(request.FILES['csv_file'].file, encoding=request.encoding).read()
        graph = models.Graph(name='CSV import of %s' % (request.FILES['csv_file'].name), links=links)
        graph.save()
        return HttpResponse(str(graph))
    return HttpResponse(templates.index(request, models.Graph.objects.all().order_by('-imported_at')))

def result(request, pk):
    graph = get_object_or_404(models.Graph, pk=pk)
    return HttpResponse(templates.result(request, graph))

def api_result(request, pk):
    graph = get_object_or_404(models.Graph, pk=pk)
    return HttpResponse(graph.links)
