from io import TextIOWrapper

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from core import templates, models, third_party_import

@login_required
def index(request):
    graph = None
    if request.POST and request.POST['action'] == 'import':
        if request.POST and request.FILES:
            links = TextIOWrapper(request.FILES['csv_file'].file, encoding=request.encoding).read()
            graph = models.Graph(name='CSV import of %s' % (request.FILES['csv_file'].name), links=links, user=request.user)
            graph.save()
        elif request.POST:
            q = request.POST['q']
            links = third_party_import.arxiv_to_csv(q)
            graph = models.Graph(name='arXiv import of search term: %s' % (q, ), links=links, user=request.user)
            graph.save()
        if graph:
            from config.celery import process_graph
            process_graph.delay(graph.pk)
            return redirect(graph)

    if request.POST and request.POST['action'] == 'delete':
        graph = get_object_or_404(models.Graph, pk=request.POST['graph_id'])
        graph.delete()
        return redirect('/')

    return HttpResponse(templates.index(request, models.Graph.objects.filter(user=request.user).order_by('-created_at')))


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

from django.contrib.auth.views import login as login_view

def login(request):
    if request.POST:
        login_view(request)
        if request.user.is_authenticated():
            return redirect('/')
    return HttpResponse(templates.login(request))

from django.contrib.auth import logout as auth_logout

def logout(request):
    auth_logout(request)
    return redirect('/')
