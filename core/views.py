from io import TextIOWrapper

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from core import templates, models, third_party_import

@login_required
def index(request):
    graph = None
    if request.POST and request.FILES:
        links = TextIOWrapper(request.FILES['csv_file'].file, encoding=request.encoding).read()
        graph = models.Graph(name='CSV import of %s' % (request.FILES['csv_file'].name), links=links)
        graph.save()
    elif request.POST:
        q = request.POST['q']
        links = third_party_import.arxiv_to_csv(q)
        graph = models.Graph(name='arXiv import of search term: %s' % (q, ), links=links)
        graph.save()
    if graph:
        from config.celery import process_graph
        process_graph.delay(graph.pk)
        return redirect(graph)
    return HttpResponse(templates.index(request, models.Graph.objects.all().order_by('-created_at')))


@login_required
def result(request, pk):
    graph = get_object_or_404(models.Graph, pk=pk)
    result = None
    try:
        result = models.ProcessingResult.objects.get(graph=graph)
    except:
        pass
    return HttpResponse(templates.result(request, graph, result))


@login_required
def api_result(request, pk):
    graph = get_object_or_404(models.Graph, pk=pk)

    data = {
        'links': graph.links,
    }

    result = None
    try:
        result = models.ProcessingResult.objects.get(graph=graph)
    except:
        pass
    if result:
        data['result'] = {
            'progress': result.progress,
            'clusters': result.clusters,
            'topics': result.topics,
        }
    return JsonResponse(data)


def login(request):
    if request.POST:
        login(request.POST['username'], request.POST['password'])
    return HttpResponse(templates.login(request, form))


def logout(request):

    return redirect('/')
