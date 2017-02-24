from io import TextIOWrapper

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from core import templates, models, third_party_import

from django.core.exceptions import PermissionDenied

@login_required
def index(request):
    messages = []
    graph = None
    if request.POST and request.POST['action'] == 'import':
        clusters, topics, valid_parameters = None, None, True
        if request.POST['clustering'] == 'manual':
            try:
                clusters = int(request.POST['clusters'])
                topics = int(request.POST['topics'])
                if clusters <= 0 or topics <= 0:
                    messages.append(['danger', 'Invalid cluster parameters'])
                    valid_parameters = False
            except ValueError:
                messages.append(['danger', 'Invalid cluster parameters']) # todo: proper form validation
                valid_parameters = False
        if valid_parameters:
            if ('choice_csv' in request.POST or 'choice_mbox' in request.POST) and not request.FILES:
                messages.append(['danger', 'You must include a file to import'])
            elif 'choice_csv' in request.POST:
                if 'csv_file' not in request.FILES:
                    messages.append(['danger', 'You must include a file to import'])
                links = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8').read()
                graph = models.Graph(name='CSV import of %s' % (request.FILES['csv_file'].name), links=links, user=request.user)
            elif 'choice_mbox' in request.POST:
                if 'mbox_file' not in request.FILES:
                    messages.append(['danger', 'You must include a file to import'])
                mbox = TextIOWrapper(request.FILES['mbox_file'].file, encoding='utf-8')
                links = third_party_import.mbox_to_csv(mbox, request.POST.get('mbox_subject_only'))
                graph = models.Graph(name='MBOX import of %s' % (request.FILES['mbox_file'].name), links=links, user=request.user)
            elif 'choice_arxiv' in request.POST:
                q = request.POST['q']
                if len(q) > 0:
                    links = third_party_import.arxiv_to_csv(q)
                    graph = models.Graph(name='arXiv import of search term: %s' % (q, ),
                        links=links, user=request.user, directed=False)
                else:
                    messages.append(['danger', 'You must include a search term to do a query'])
            elif 'choice_hal' in request.POST:
                q = request.POST['q']
                if len(q) > 0:
                    links = third_party_import.hal_to_csv(q)
                    graph = models.Graph(name='HAL import of search term: %s' % (q, ),
                        links=links, user=request.user, directed=False)
                else:
                    messages.append(['danger', 'You must include a search term to do a query'])
            if graph:
                if len(graph.links.strip()) < 2:
                    messages.append(['danger', 'There is no data for this graph'])
                else:
                    graph.save()
                    from config.celery import process_graph
                    process_graph.delay(graph.pk, clusters, topics)
                    return redirect(graph)

    if request.POST and request.POST['action'] == 'delete':
        graph = get_object_or_404(models.Graph, pk=request.POST['graph_id'])
        graph.delete()
        return redirect('/')

    return HttpResponse(templates.index(
        request,
        models.Graph.objects.filter(user=request.user).order_by('-created_at'),
        messages,
    ))

@login_required
def result(request, pk):
    graph = get_object_or_404(models.Graph, pk=pk)
    if request.user.pk != graph.user.pk:
        raise PermissionDenied
    result = None
    try:
        result = models.ProcessingResult.objects.get(graph=graph)
    except:
        pass
    return HttpResponse(templates.result(request, graph, result))

@login_required
def api_result(request, pk):
    graph = get_object_or_404(models.Graph, pk=pk)
    if request.user.pk != graph.user.pk:
        raise PermissionDenied
    result = None
    try:
        result = models.ProcessingResult.objects.get(graph=graph)
    except:
        pass
    return JsonResponse(templates.api_result(request, graph, result))

from django.contrib.auth.views import login as login_view

def login(request):
    message = None
    if request.POST:
        login_view(request)
        if request.user.is_authenticated():
            return redirect('/')
        else:
            message = "Please enter a correct username and password"
    return HttpResponse(templates.login(request, message))

from django.contrib.auth import logout as auth_logout

def logout(request):
    auth_logout(request)
    return redirect('/')
