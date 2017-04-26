from io import TextIOWrapper
import hashlib

from django import forms
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.conf import settings

from raven.contrib.django.raven_compat.models import client
import TwitterAPI

from core import templates, models, third_party_import

MAX_JOBS_PER_USER = 10

@login_required
def index(request):
    from config.celery import import_graph_data, retrieve_graph_data

    if models.Graph.objects.filter(user=request.user).count() > MAX_JOBS_PER_USER:
        messages = [('danger', 'You are limited to %d jobs, please delete previous ones before importing a new one' % MAX_JOBS_PER_USER)]
        return HttpResponse(templates.index(
            request,
            messages,
            '__no_import_type__',
            quota_exceeded=True,
        ))

    messages = []
    graph = None
    if request.POST and request.POST['action'] == 'import':
        clusters, topics, limit, valid_parameters = None, None, 200, True
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
        try:
            limit = int(request.POST.get('limit', limit))
            limit = min(limit, 1000)
        except ValueError:
            messages.append(['danger', 'Invalid limit']) # todo: proper form validation
            valid_parameters = False
        if valid_parameters:

            def make_graph(name, directed=True):
                graph = models.Graph(name=name,
                    user=request.user, directed=directed)
                if clusters:
                    graph.job_param_clusters = clusters
                    graph.job_param_clusters_max = clusters
                    graph.job_param_topics = topics
                    graph.job_param_topics_max = topics
                graph.save()
                return graph

            def papers_import(name, method, **kwargs):
                graph = make_graph(name, directed=kwargs.get('directed', False))
                retrieve_graph_data.delay(graph.pk, method, **kwargs)
                return redirect('/jobs/')

            if ('choice_csv' in request.POST or 'choice_mbox' in request.POST) and not request.FILES:
                messages.append(['danger', 'You must include a file to import'])

            elif 'choice_csv' in request.POST:
                if 'csv_file' not in request.FILES:
                    messages.append(['danger', 'You must include a file to import'])
                links = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8').read()
                graph = make_graph('CSV import of %s' % (request.FILES['csv_file'].name))
                import_graph_data.delay(graph.pk, links)
                return redirect('/jobs/')

            elif 'choice_mbox' in request.POST:
                if 'mbox_file' not in request.FILES:
                    messages.append(['danger', 'You must include a file to import'])
                graph = make_graph('MBOX import of %s' % (request.FILES['mbox_file'].name))
                
                mbox = TextIOWrapper(request.FILES['mbox_file'].file, encoding='utf-8')
                # TODO async conversion to csv
                links = third_party_import.mbox_to_csv(mbox, request.POST.get('mbox_subject_only'))
                import_graph_data.delay(graph.pk, links)
                return redirect('/jobs/')

            elif 'choice_arxiv' in request.POST:
                q = request.POST['q']
                if len(q) > 0:
                    return papers_import(
                        'arXiv import of search term: %s' % (q, ),
                        'arxiv_to_csv',
                        q=q, limit=limit
                    )
                else:
                    messages.append(['danger', 'You must include a search term to do a query'])
            elif 'choice_twitter' in request.POST:
                q = request.POST['q']
                if len(q) > 0:
                    name = 'Twitter import of search term: %s' % (q, )
                    if request.POST.get('use_loklak'):
                        return papers_import(
                            name,
                            'loklak_to_csv',
                            q=q, limit=limit
                        )
                    else:
                        # TODO capture exception inside celery job
                        try:
                            return papers_import(
                                name,
                                'twitter_to_csv',
                                q=q, limit=limit,
                                ignore_self_loop=False,
                                directed=True
                            )
                        except TwitterAPI.TwitterRequestError as e:
                            messages.append(['danger', str(e)])
                            links = ''
                else:
                    messages.append(['danger', 'You must include a search term to do a query'])
            elif 'choice_hal' in request.POST:
                q = request.POST['q']
                if len(q) > 0:
                    return papers_import(
                        'HAL import of search term: %s' % (q, ),
                        'hal_to_csv',
                        q=q, limit=limit
                    )
                else:
                    messages.append(['danger', 'You must include a search term to do a query'])
            elif 'choice_pubmed' in request.POST:
                q = request.POST['q']
                if len(q) > 0:
                    return papers_import(
                        'PubMed import of search term: %s' % (q, ),
                        'pubmed_to_csv',
                        q=q, limit=limit
                    )
                else:
                    messages.append(['danger', 'You must include a search term to do a query'])
            elif 'choice_dropdown' in request.POST:
                filename = request.POST['sample_dropdown']
                assert '/' not in filename
                if '.mbox' in filename:
                    content = open('csv_samples/' + filename).readlines()
                    links = third_party_import.mbox_to_csv(content, subject_only=False)
                    data = models.graph_data_from_links(links)
                    graph = models.Graph(name='MBOX import of %s' % (filename), user=request.user, **data)
                elif '.csv' in filename:
                    content = open('csv_samples/' + filename).read()
                    graph = make_graph('CSV import of %s' % (filename))
                    import_graph_data.delay(graph.pk, content)
                    return redirect('/jobs/')
            if graph:
                if len(graph.labels.strip()) < 2:
                    messages.append(['danger', 'There is no data for this graph'])
                else:
                    if clusters:
                        graph.job_param_clusters = clusters
                        graph.job_param_clusters_max = clusters
                        graph.job_param_topics = topics
                        graph.job_param_topics_max = topics
                    graph.save()

                    from config.celery import process_graph
                    process_graph.delay(graph.pk, ws_delay=2)
                    return redirect('/jobs/')

    return HttpResponse(templates.index(
        request,
        messages,
        request.GET.get('import_type')
    ))

@login_required
def result(request, pk):
    graph = get_object_or_404(models.Graph, pk=pk)
    if request.user.pk != graph.user.pk:
        raise PermissionDenied
    result = None
    try:
        result = models.ProcessingResult.objects \
            .filter(graph=graph) \
            .order_by('-crit') \
            .first()
    except:
        pass
    return HttpResponse(templates.result(request, graph, result))


@login_required
def details(request, pk):
    graph = get_object_or_404(models.Graph, pk=pk)
    if request.user.pk != graph.user.pk:
        raise PermissionDenied
    results = models.ProcessingResult.objects \
            .filter(graph=graph) \
            .order_by('-crit')
    return HttpResponse(templates.details(request, graph, results))


def landing(request):
    if 'confirm_email_token' in request.GET:
        user_pk, token = request.GET['confirm_email_token'].split('p', 1)
        user = User.objects.get(pk=int(user_pk))
        if get_user_token(user) == token and not user.is_active:
            user.is_active = True
            user.save()
            auth_login(request, user)
            messages.success(request, 'Account %s confirmed' % user.email)
        return redirect('/')
    return HttpResponse(templates.landing(request))


def terms(request):
    return HttpResponse(templates.terms(request))


@login_required
def jobs(request):
    if request.POST and request.POST['action'] == 'delete':
        graph = get_object_or_404(models.Graph, pk=request.POST['graph_id'])
        graph.delete()

    jobs = models.Graph.objects.filter(user=request.user).order_by('-created_at')

    if request.GET.get('as_json'):
        return JsonResponse(templates.api_jobs(jobs), safe=False) # TODO: review safe=False

    return HttpResponse(templates.jobs(
        request,
        models.Graph.objects.filter(user=request.user).order_by('-created_at'),
    ))

def addjob(request):
    return index(request)

@login_required
def api_result(request, pk):
    graph = get_object_or_404(models.Graph, pk=pk)
    if request.user.pk != graph.user.pk:
        raise PermissionDenied

    result = None

    try:
        clusters = int(request.GET['clusters'])
        topics = int(request.GET['topics'])
        result = models.ProcessingResult.objects \
            .get(graph=graph,
                param_clusters=clusters,
                param_topics=topics)
    except:
        print('no match for clusters/topics')

    if not result:
        try:
            result = models.ProcessingResult.objects \
                .filter(graph=graph) \
                .order_by('-crit')
            if 'all' not in request.GET:
                result = result.first()
        except:
            print('no match for graph')
    
    if 'zip' in request.GET:
        return HttpResponse(models.export_to_zip(graph, result),
                content_type='application/zip')

    return JsonResponse(templates.api_result(request, graph, result))


@login_required
def api_cluster(request, pk):
    graph = get_object_or_404(models.Graph, pk=pk)
    if request.user.pk != graph.user.pk:
        raise PermissionDenied

    if 'cluster_to_cluster_cutoff' in request.POST:
        graph.cluster_to_cluster_cutoff = float(cluster_to_cluster_cutoff)
        graph.save()
        return JsonResponse({'message': 'ok [cutoff-updated]'})

    clusters = int(request.POST['clusters'])
    topics = int(request.POST['topics'])
    if clusters <= 0 or topics <= 0:
        return JsonResponse({'message': 'error: invalid parameters'})

    result = None
    try:
        result = models.ProcessingResult.objects.get(graph=graph,
            param_clusters=clusters,
            param_topics=topics)
        if result:
            return JsonResponse({
                'message': 'ok [already-clustered]',
                'result': templates.api_result(request, graph, result)['result'],
            })
    except Exception as e: 
        print(e)

    return JsonResponse({'message': 'nok [dynamic-clustering-disabled]'})

    result = models.ProcessingResult(graph=graph, param_clusters=clusters, param_topics=topics)
    result.save()

    from config.celery import process_graph
    process_graph.delay(graph.pk, result.pk, ws_delay=0)

    return JsonResponse({'message': 'ok [clustering-launched]'})


from django.contrib.auth.views import login as login_view

def login(request):
    message = None
    if request.POST:
        login_view(request)
        if request.user.is_authenticated():
            return redirect('/jobs/add/')
        else:
            message = "Please enter a correct username and password"
    return HttpResponse(templates.login(request, message, SignupForm()))

class SignupForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True)
    org = forms.CharField(required=True)

# TODO: get rid of homemade protocol and get a real random token
def get_user_token(user):
    return hashlib.sha512(('%s %s %s' % (user.pk, user.email, settings.SECRET_KEY)).encode()).hexdigest()

def signup(request):
    message = None
    form = SignupForm()
    if request.method == 'POST':
        form = SignupForm(data=request.POST)
        if form.is_valid():
            email, password = form.cleaned_data['email'], form.cleaned_data['password']
            email_domain = email.split('@')[1]
            if email_domain not in ('parisdescartes.fr', 'univ-paris1.fr', 'dam.io'):
                message = 'Email domain is restricted during the beta period, please contact us if you want an account'
            else:
                user = User.objects.create_user(email, email, password)
                models.UserProfile(user=user, org_type=form.cleaned_data['org']).save()
                user.is_active = False
                user.save()

                try:
                    raise Exception('User created: {}'.format(email))
                except:
                    client.captureException()

                token = str(user.pk) + 'p' + get_user_token(user)

                send_mail('[linkage.fr] Account confirmation', """Welcome to linkage.fr.

You are just one click away from getting an account, click on the following link to confirm your account:
https://linkage.fr/?confirm_email_token=%s
""" % token, 'no-reply@linkage.fr', [email], fail_silently=False)

                messages.success(request, 'An email has been sent to %s to confirm the account creation' % email)

                return redirect('/')
        else:
            message = 'Invalid email/password'

    return HttpResponse(templates.signup(request, form, message))

from django.contrib.auth import logout as auth_logout

def logout(request):
    auth_logout(request)
    return redirect('/')
