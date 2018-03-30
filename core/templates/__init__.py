import random, csv, json, sys, os

from django.middleware.csrf import get_token
from django.contrib.humanize.templatetags.humanize import naturaltime, naturalday
from django.template.defaultfilters import filesizeformat
from django.conf import settings
from django.contrib.messages import get_messages
from django.urls import reverse

import mistune
import natural.date
from lys import L, raw

from .base import base

csv.field_size_limit(sys.maxsize)  # http://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072
DEBUG = settings.DEBUG
COMMIT_HASH = settings.COMMIT_HASH

SPACER = raw('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')  # dat spacer
SHORT_SPACER = raw('&nbsp;&nbsp;')


def icon(name):
    return L.span('.glyphicon.glyphicon-' + name)


def header(request, page_name=''):
    return L.div('.row') / (
        L.div('.col-xs-3' if settings.LINKAGE_ENTERPRISE else '.col-xs-2') / (
            L.a(href='/') / (
                L.h2 / (
                    'Linkage',
                    (L.small / ' Enterprise') if settings.LINKAGE_ENTERPRISE else '',
                    # '*' if DEBUG else None
                ),
            ),
        ),
        L.div('.col-xs-4' if settings.LINKAGE_ENTERPRISE else '.col-xs-5') / (
            L.ul('.nav.nav-pills') / (
                L.li('.active' if page_name == 'addjob' else '',
                        style='margin-top: 20px;margin-right: 20px;display:inline-block') / (
                    L.a(href='/jobs/add/') / 'New Job',
                ),
                L.li('.active' if page_name == 'jobs' else '',
                        style='margin-top: 20px;display:inline-block') / (
                    L.a(href='/jobs/') / 'Jobs',
                ),
            ),
        ) if request.user.is_authenticated else None,
        L.div('.col-xs-5.text-right') / (
            L.span('.btn.btn-link.disabled', style='margin-top: 20px;display:inline-block') / request.user.username,
            (
                L.a('.btn.btn-link', href='/admin/', style='margin-top: 20px;display:inline-block') / 'admin'
            ) if request.user.is_superuser or request.user.is_staff else None,
            L.a('.btn.btn-link', href='/accounts/logout/', style='margin-top: 20px;display:inline-block') / 'logout',
        ) if request.user.is_authenticated else None,
    ), L.hr(style='margin-top:5px;margin-bottom:15px')


FOOTER = (
    L.div('.row') / (
        L.div('.col-sm-12 text-center') / (
            L.div / (
                L.hr,
                L.a(href='http://www.parisdescartes.fr/') / L.img(src='/static/img/descartes.png', height='60'),
                SPACER,
                L.a(href='http://map5.mi.parisdescartes.fr/') / L.img(src='/static/img/map5.jpg', height='60'),
                SPACER,
                L.a(href='http://www.cnrs.fr/') / L.img(src='/static/img/cnrs.png', height='60'),
                SPACER,
                L.a(href='http://www.idfinnov.com/') / L.img(src='/static/img/idfinnov.jpg', height='60'),
                SPACER,
                L.a(href='http://samm.univ-paris1.fr/') / L.img(src='/static/img/samm.png', height='60'),
                SPACER,
                L.a(href='https://www.univ-paris1.fr/') / L.img(src='/static/img/paris1.png', height='60'),
            ),
            L.br,
            L.div / (
                L.a(href='/about/terms/') / 'Terms and conditions',
                SPACER,
                L.a(href='/about/credits/') / 'Credits',
            ) if not settings.LINKAGE_ENTERPRISE else (
                L.a(href='/about/terms/') / 'Terms and conditions for Enterprise',
            ),
            L.br,
            L.br,
        ),
    ),
)

SENTRY = []
if not DEBUG:
    SENTRY = (
        L.script(src='/static/js/vendor/raven.min.js'),
        L.script / raw("Raven.config('https://630be20fb2e64d309af37490c264fefa@sentry.io/142095').install()"),
    )

JS_LIBS = (
        SENTRY,
        L.script(src='/static/js/vendor/jquery.js'),
        L.script(src='/static/js/vendor/tether.js'),
        L.script(src='/static/js/vendor/bootstrap.js'),
)


def top_nodes_per_clusters(graph, result):
    labels = list(csv.reader([graph.labels], delimiter=' '))[0]
    clusters = [int(x) for x in 
        list(csv.reader([result.clusters_mat], delimiter=' '))[0]
        if x is not '']

    clusters_nodes = {}

    def add_one(node):
        cluster = clusters[node]
        if cluster not in clusters_nodes:
            clusters_nodes[cluster] = {}
        clust_nodes = clusters_nodes[cluster]
        if node not in clust_nodes:
            clust_nodes[node] = 0
        clust_nodes[node] += 1

    for line in csv.reader(graph.edges.split('\n'), delimiter=' '):
        if len(line) == 3:
            source, target, val = line
            if val == '0':
                continue
            add_one(int(source))
            add_one(int(target))

    def top_10(cluster):
        nodes = clusters_nodes.get(cluster, {})
        return [labels[node] for node, _ in
                    sorted(nodes.items(), key=lambda it: -it[1]) #[:10]
                ]
    top_nodes = [top_10(cluster) for cluster in range(max(clusters) + 1)]

    return top_nodes # [ [label1_for_cluster_1, label2], [label4_for_cluster_2, label3],.. ]


def serialize_graph(graph, result, simple=False, scores=None):
    data = {
        'id': graph.pk,
        'user': graph.user.pk,
        'name': graph.name,
        'labels': graph.labels,
        'edges': graph.edges,
        'n_edges': len(graph.edges.split('\n')),
        'n_labels': len(list(csv.reader([graph.labels], delimiter=' '))[0]),
        'tdm': graph.tdm,
        'public': graph.public,
        'dictionnary': graph.dictionnary,
        'directed': graph.directed,
        'created_at': naturaltime(graph.created_at),
        'url': graph.get_absolute_url(),
        'log': graph.job_log,
        'step': graph.job_current_step,
        'time_t': graph.job_time,
        'time': natural.date.compress(graph.job_time * 100),
        'progress': graph.job_progress,
        'cluster_to_cluster_cutoff': graph.cluster_to_cluster_cutoff,
        'job_param_clusters': graph.job_param_clusters,
        'job_param_topics': graph.job_param_topics,
        'job_param_clusters_max': graph.job_param_clusters_max,
        'job_param_topics_max': graph.job_param_topics_max,
        'job_error_log': graph.job_error_log,
        'magic_too_big_to_display_X': graph.magic_too_big_to_display_X,
        'scores': scores,
        'has_original_csv': len(graph.original_csv) > 0,
    }
    if graph.magic_too_big_to_display_X:
        data['edges'] = '0 0 1'
        data['labels'] = '0 0'
    if simple:
        del data['tdm']
        del data['dictionnary']
        del data['labels']
        del data['edges']
        del data['log']
    if result:
        try:
            # for export
            if len(result) > 1:
                data['results'] = [r.serialize() for r in result]
        except TypeError:
            data['result'] = result.serialize()
            data['result']['top_nodes'] = top_nodes_per_clusters(graph, result)
            if graph.magic_too_big_to_display_X:
                data['topics_per_edges_mat'] = '0 0 1'
    return data


def result(request, graph, result, scores):
    return base((
        L.div('.container-fluid') / (
            header(request),
            (L.div('.row') / (
                L.div('col-sm-12') / (
                    L.div('.alert.alert-warning') / "This is a preview of a result too large to be fully displayed",
                ),
            ) if graph.magic_too_big_to_display_X else None),
            L.div('.row') / (
                L.div('.col-sm-3') / (
                    L.div('#_sidebar'),
                ),
                L.div('.col-sm-9') / (
                    L.div('#_graph-tabs'),
                    L.br,
                    L.div('#_graph-panel.panel.panel-default', style='position:relative') / (
                        L.div('#_graph-sidebar'),
                        L.div('#_graph-buttons'),
                        L.div('.panel-body', style='padding:0') / (
                            L.h3('#_loading.text-center') / 'Loading…',
                            L.div('#_graph'),
                        ),
                    ),
                    L.div('#_matrix-viz-panel.panel.panel-default.hide.text-center', style='position:relative') / (
                        L.div('#_matrix-viz'),
                    ),
                    L.div('#_viz-panel.panel.panel-default.hide', style='position:relative') / (
                        L.div('row.text-center') / (
                            (L.div('col-sm-6') / (
                                L.h4 / 'Nodes per cluster',
                                L.br,
                                L.div('#_bar-plot', style="width:100%;height:400px;display: inline-block;"),
                            )) if graph.magic_too_big_to_display_X else (
                                L.div('col-sm-6') / (
                                    L.h4 / 'Nodes per cluster',
                                    L.br,
                                    L.div('#_bar-plot', style="width:100%;height:400px;display: inline-block;"),
                                ),
                                L.div('col-sm-6') / (
                                    L.h4 / 'Topics',
                                    L.br,
                                    L.div('#_topics-bar-plot', style="width:100%;height:400px;display: inline-block;"),
                                ),
                            )
                        ),
                        L.hr,
                        L.div('#_words-plot'),
                    ),
                ),
            ),
            FOOTER,
        ),
        JS_LIBS,
        L.script / raw("var USER_ID = %d;" % (request.user.pk if request.user.pk else -1,)),
        L.script(src='/static/js/vendor/vivagraph.js'),
        L.script(src='/static/js/vendor/papaparse.js'),
        L.script(src='/static/js/vendor/plotly-latest.min.js'),
        L.script / raw("var GRAPH = {};".format(json.dumps(serialize_graph(graph, result, scores=scores)))),
        L.script(src='/static/js/dist/vendor.js?v=' + COMMIT_HASH),
        L.script(src='/static/js/dist/graph.js?v=' + COMMIT_HASH),
    ), title=graph.name)


def api_result(request, graph, result):
    return serialize_graph(graph, result)


def index(request, messages, import_type_selected='coauth', quota_exceeded=False, user_jobs=None, gmail_access_accepted=False):
    if not import_type_selected:
        import_type_selected = 'coauth'
    return base((
        L.div('.container') / (
            header(request, 'addjob'),
            L.div('.row') / (
                L.div('.col-sm-12') / (
                    L.h4 / 'Import from',
                ),
            ),
            L.div('.row') / (
                L.div('.col-sm-3') / (
                    L.div('.list-group') / (
                        L.a('.list-group-item' + ('.active' if import_type_selected == 'coauth' else ''),
                            href='?import_type=coauth') / 'Papers co-authorship network',
                        (
                            (L.a('.list-group-item' + ('.active' if import_type_selected == 'gmail' else ''),
                                href='?import_type=gmail') / 'GMail')
                        ) if not settings.LINKAGE_ENTERPRISE else '',
                        L.a('.list-group-item' + ('.active' if import_type_selected == 'mbox' else ''),
                            href='?import_type=mbox') / 'MBox file',
                        L.a('.list-group-item' + ('.active' if import_type_selected == 'twitter' else ''),
                            href='?import_type=twitter') / 'Twitter search',
                        L.a('.list-group-item' + ('.active' if import_type_selected == 'csv' else ''),
                            href='?import_type=csv') / 'Your own network (CSV)',
                        L.a('.list-group-item' + ('.active' if import_type_selected == 'sample' else ''),
                            href='?import_type=sample') / 'Demonstration dataset',
                        (L.a('.list-group-item' + ('.active' if import_type_selected == 'prev_job' else ''),
                            href='?import_type=prev_job') / 'Existing job') if user_jobs else None,
                    ),
                ),
                L.div('.col-sm-9') / (
                    (L.div('.alert.alert-' + msgtype) / msg for msgtype, msg in messages),
                    L.form('.row.form-horizontal', method="post", enctype="multipart/form-data") / (
                        L.input(type='hidden', name='csrfmiddlewaretoken', value=get_token(request)),
                        L.input(type='hidden', name='action', value='import'),
                        (
                            L.div('.row') / (
                                L.div('.col-sm-5') / L.input('.form-control', type='text', name='q', placeholder="'Deep Learning', 'Speech Synthesis', 'qubit', 'graphene',…"),
                                L.div('.col-sm-7') / (
                                    L.input('.btn.btn-success', name='choice_arxiv', type='submit', value='search arXiv'),
                                    SPACER,
                                    L.input('.btn.btn-success', name='choice_hal', type='submit', value='search HAL'),
                                    ' ',
                                    L.a('.label.label-default',
                                        href='https://api.archives-ouvertes.fr/docs/search/#q',
                                        data_balloon_pos="bottom",
                                        data_balloon="See documentation to learn more about the parameters you can use for HAL") / '?',
                                    SPACER,
                                    L.input('.btn.btn-success', name='choice_pubmed', type='submit', value='search PubMed'),
                                )
                            ),
                            L.br,
                            L.div('.form-group') / (
                                L.div('.col-sm-3.control-label') / (
                                    L.strong / (
                                        L.abbr(title='The maximum number of papers to be retrieved') / 'Limit',
                                    ),
                                ),
                                L.div('.col-sm-2') / (
                                    L.input('.form-control', name='limit', value='500', type='number', max='10000'),
                                ),
                            ),
                        ) if import_type_selected == 'coauth' else None,
                        (
                            L.div('.row') / (
                                L.div('.col-sm-5') / L.input('.form-control', type='text', name='q', placeholder="@spotify, #fakenews,…"),
                                L.div('.col-sm-7') / (
                                    L.input('.btn.btn-success', name='choice_twitter', type='submit', value='search'),
                                )
                            ),
                            L.br,
                            L.div('.form-group._mbox-options') / (
                                L.div('.col-sm-3.control-label') / (' '),
                                L.div('.col-sm-9') / (
                                    L.div('.checkbox') / (
                                        L.label / (
                                            L.input(name='use_loklak', type='checkbox'),
                                            ' Use loklak API - ',
                                            L.i / 'the twitter API is limited to the tweets for the last 7 days, by using the loklak API you can get older tweets but not all of them are indexed there',
                                        )                                    
                                    ),                                 
                                ),
                            ),
                            L.div('.form-group') / (
                                L.div('.col-sm-3.control-label') / (
                                    L.strong / (
                                        L.abbr(title='The maximum number of tweet to be retrieved') / 'Limit',
                                    ),
                                ),
                                L.div('.col-sm-2') / (
                                    L.input('.form-control', name='limit', value='500', type='number', max='10000'),
                                ),
                            ),
                        ) if import_type_selected == 'twitter' else None,
                        (
                            L.div('.row') / (
                                L.div('.col-sm-7') / L.input('form-control', type='file', name='csv_file'),
                                L.div('.col-sm-5') / (
                                    L.input('.btn.btn-success',
                                        data_balloon_pos="bottom",
                                        data_balloon="A list of edges formatted like this: 'node1,node2,text'",
                                        name='choice_csv', type='submit', value='Import .csv'),
                                    ' ',
                                    L.span('.label.label-default',
                                        data_balloon_pos="bottom",
                                        data_balloon="A list of edges formatted like this: 'node1,node2,text'") / '?',
                                )
                            ),
                        ) if import_type_selected == 'csv' else None,
                        (
                            L.div('.row') / (
                                L.div('.col-sm-7') / L.input('form-control', type='file', name='mbox_file'),
                                L.div('.col-sm-5') / (
                                    L.input('.btn.btn-success', name='choice_mbox', type='submit', value='Import .mbox'),
                                )
                            ),
                            L.div('.form-group._mbox-options') / (
                                L.div('.col-sm-3.control-label') / (' '),
                                L.div('.col-sm-9') / (
                                    L.div('.checkbox') / (
                                        L.label / (
                                            L.input(name='mbox_subject_only', checked='', type='checkbox'),
                                            ' Import email subjects only'
                                        )                                    
                                    ),                                 
                                ),
                            ),
                        ) if import_type_selected == 'mbox' else None,
                        (
                            L.div('.row') / (
                                L.div('.col-sm-7') / (
                                    L.select('.form-control', name='sample_dropdown') / (
                                        (
                                            L.option(value=filename) / (
                                                filename,
                                                ' (',
                                                filesizeformat(os.stat('csv_samples/' + filename).st_size),
                                                ')',
                                            )
                                        ) for filename in sorted(os.listdir('csv_samples/'))
                                    )
                                ),
                                L.div('.col-sm-5') / (
                                    L.input('.btn.btn-success', name='choice_dropdown', type='submit', value='Import'),
                                )
                            ),
                        ) if import_type_selected == 'sample' else None,
                        (
                            L.div('.row') / (
                                L.div('.col-sm-2') / (
                                ),
                                L.div('.col-sm-5.text-center') / (
                                    (
                                        L.input('.btn.btn-success', name='choice_gmail', type='submit', value='Import from GMail'),
                                        # L.br,
                                        # L.br,
                                        # L.a('.btn.btn-warning.btn-sm', href=reverse('social:disconnect', args=['google-gmail']) + '?next=/jobs/add/?import_type=gmail') / 'Disconnect your GMail account from Linkage',
                                    ) if gmail_access_accepted else (
                                        L.a('.btn.btn-default', href=reverse('social:begin', args=['google-gmail']) + '?next=/jobs/add/?import_type=gmail') / 'Authorize Linkage to access your emails',
                                    )
                                )
                            ),
                            L.br,
                            L.div('.form-group') / (
                                L.div('.col-sm-3.control-label') / (
                                    L.strong / (
                                        L.abbr(title='The maximum number of papers to be retrieved') / 'Limit',
                                    ),
                                ),
                                L.div('.col-sm-2') / (
                                    L.input('.form-control', name='limit', value='500', type='number', max='10000'),
                                ),
                            ),
                        ) if import_type_selected == 'gmail' else None,
                        (
                            L.div('.row') / (
                                L.div('.col-sm-7') / (
                                    L.select('.form-control', name='job_dropdown') / (
                                        (
                                            L.option(value=str(job.pk)) / str(job)
                                        ) for job in user_jobs
                                    )
                                ),
                                L.div('.col-sm-5') / (
                                    L.input('.btn.btn-success', name='choice_prev_job', type='submit', value='Import'),
                                ),
                            ),
                        ) if import_type_selected == 'prev_job' and user_jobs else None,
                        L.hr,
                        L.div('.form-group') / (
                            L.div('.col-sm-3.control-label') / (L.strong / 'Clustering'),
                            L.div('.col-sm-9') / (
                                L.div('.radio') / (
                                    L.label / (
                                        L.input(name='clustering', value='auto', checked='', type='radio'),
                                        L.abbr(title='scan between 2 and 5 clusters and topics (slow)') / 'Auto',
                                    ),
                                ),
                                L.div('.radio') / (
                                    L.label / (
                                        L.input(name='clustering', value='manual', type='radio'),
                                        L.abbr(title='Scan your own range of topic/cluster (fast)') / 'Custom range',
                                    ),
                                )
                            ),
                        ),
                        L.div('.form-group._mbox-options') / (
                            L.div('.col-sm-3.control-label') / (' '),
                            L.div('.col-sm-9') / (
                                L.div('.checkbox') / (
                                    L.label / (
                                        L.input(name='filter_largest_subgraph', type='checkbox', checked='true') if import_type_selected in ('twitter', 'coauth')
                                            else L.input(name='filter_largest_subgraph', type='checkbox'),
                                        ' Only keep the largest subgraph from the graph',
                                    )                                    
                                ),                                 
                            ),
                        ),
                        L.div('.form-group._clustering-options.hide') / (
                            L.div('#_slider_clusters'),
                        ),
                        L.div('.form-group._clustering-options.hide') / (
                            L.div('#_slider_topics'),
                        ),
                    ) if not quota_exceeded else None,
                ),
            ),
            FOOTER
        ),
        JS_LIBS,
        L.script(src='/static/js/dist/vendor.js?v=' + COMMIT_HASH),
        L.script(src='/static/js/dist/import.js?v=' + COMMIT_HASH),
    ))


def _very_basic_captcha():
    x = random.randint(1, 10)
    y = random.randint(1, 10)
    return L.div('.form-group') / (
        L.label('.control-label') / (
            L.abbr(title='Simple question to prevent automated registration') / 'Captcha ',
        ),
        L.div / (
            L.i / (
                str(x), ' + ', str(y), ' = ',
            ),
            L.input(type='hidden', name='simple_captcha_answer', value=str(x+y)),
            L.input('.form-control.input-sm', name='simple_captcha', style='display:inline;width:40%'),
        ),
    )


def login(request, message, signup_form):
    return base((
        L.div('.container') / (
            header(request),
            L.div('.row') / (
                L.div('.col-sm-6.center-block', style='float:none') / (
                    L.div('.alert.alert-info') / (
                        'You need to login to access this application' if settings.LINKAGE_ENTERPRISE else
                            'You need to login or sign up to access this application'
                    ),
                    L.div('.row') / (
                        L.div('.col-sm-4.col-sm-offset-4'  if settings.LINKAGE_ENTERPRISE else '.col-sm-5') / (
                            L.h3 / 'Login',
                            (L.div('.alert.alert-danger') / message) if message else None,
                            L.form(method='post') / (
                                L.input(type='hidden', name='csrfmiddlewaretoken', value=get_token(request)),
                                L.div('.form-group') / (
                                    L.label('control-label') / 'Username',
                                    L.input('form-control', name='username'),
                                ),
                                L.div('.form-group') / (
                                    L.label('control-label') / 'Password',
                                    L.input('form-control', type='password', name='password'),
                                ),
                                L.div('.form-group.text-center') / (
                                    L.button('.btn.btn-primary', type='submit') / 'Login'
                                ),
                            ),
                            L.p('.text-center') / (
                                L.small / (
                                    L.a(href='mailto:contact@linkage.fr?subject=Password%20reset&body=Hi%2C%20could%20you%20please%20reset%20my%20password%20%3F%0A%0AThanks') / 'forgot your password ?'
                                )
                            ),
                            L.br,
                            L.p('.text-center') / (
                                L.a(href=reverse('social:begin', args=['google-oauth2'])) / 
                                    L.img('.google-signin', style='width:100%; height:auto'),
                            ) if not settings.LINKAGE_ENTERPRISE else '',
                        ),

                        L.div('.col-sm-2') / (
                            L.h3 / 'or',
                        ) if not settings.LINKAGE_ENTERPRISE else '',

                        L.div('.col-sm-5') / (
                            L.h3 / 'Sign up',
                            L.form(method='post', action='/accounts/signup/') / (
                                L.input(type='hidden', name='csrfmiddlewaretoken', value=get_token(request)),
                                L.div('.form-group') / (
                                    L.label('.control-label') / 'Email',
                                    L.input('.form-control', name='email', value=signup_form.data.get('email', '')),
                                ),
                                L.div('.form-group') / (
                                    L.label('.control-label') / 'Password',
                                    L.input('.form-control', type='password', name='password', value=signup_form.data.get('password', '')),
                                ),
                                _very_basic_captcha(),
                                L.div('.form-group') / (
                                    L.div('.checkbox') / (
                                        L.label / (
                                            L.input(name='accept_terms', checked='', type='checkbox'),
                                            ' Accept', 
                                        ),
                                        raw('&nbsp'),
                                        L.a(href='/about/terms/') / 'terms and conditions',
                                    ),
                                ),
                                L.div('.form-group.text-center') / (
                                    L.button('.btn.btn-primary', type='submit') / 'Sign up'
                                )
                            ),
                        ) if not settings.LINKAGE_ENTERPRISE else '',
                    ),
                ),
            ),
            FOOTER,
            SENTRY,
        ),
    ))


def signup(request, form, message):
    return base((
        L.div('.container') / (
            header(request),
            L.div('.row') / (
                L.div('.col-sm-3.center-block', style='float:none') / (
                    L.h3 / 'Sign up',
                    (L.div('.alert.alert-danger') / message) if message else None,
                    L.form(method='post') / (
                        L.input(type='hidden', name='csrfmiddlewaretoken', value=get_token(request)),
                        L.div('.form-group') / (
                            L.label('.control-label') / 'Email',
                            L.input('.form-control', name='email', value=form.data.get('email', '')),
                        ),
                        L.div('.form-group') / (
                            L.label('.control-label') / 'Password',
                            L.input('.form-control', type='password', name='password', value=form.data.get('password', '')),
                        ),
                        _very_basic_captcha(),
                        L.div('.form-group') / (
                            L.div('.checkbox') / (
                                L.label / (
                                    L.input(name='accept_terms', checked='', type='checkbox'),
                                    ' Accept', 
                                ),
                                raw('&nbsp'),
                                L.a(href='/about/terms/') / 'terms and conditions',
                            ),
                        ),
                        L.div('.form-group.text-center') / (
                            L.button('.btn.btn-primary', type='submit') / 'Sign up'
                        )
                    ),
                ),
            ),
            FOOTER,
            SENTRY,
        ),
    )
)


def intro(request, form, message):
    return base((
        L.div('.container') / (
            header(request),
            L.div('.row') / (
                L.div('.col-sm-6.center-block', style='float:none') / (
                    L.p / raw(mistune.markdown("""
## Before you begin

Let's explain a few things about Linkage.

<br/>
<div class='text-center'><img src='/static/img/graph.png'/></div>
<br/>

It starts with a **graph**: A network of **nodes** connected by **edges**

For example, if we want to represent an email network, we could have **email addresses** as nodes and **emails** as edges.

Linkage specificity is to process graphs with **text on the edges**, here the text could be the emails contents.

#### Clustering

When you give this graph to Linkage, it's gonna **cluster** it: It's gonna find **topics of discussion** and **groups of nodes** (clusters).

Each edge is then assigned a percentage of each topic, for example, an email can be 80% about the "surfing" topic but also 20% about the "friends" topic.

To make it easier to vizualize the results, Linkage shows you a **meta-network** where the nodes are grouped by clusters so you can easily interpret the interactions between clusters.

#### And that's Linkage for you

So, go ahead, choose the type of user you are and then you can start clustering graphs via the "New Job" page.
                    """, escape=False)),
                    L.form(method='post') / (
                        L.input(type='hidden', name='csrfmiddlewaretoken', value=get_token(request)),
                        L.div('.form-group') / (
                            L.label('.control-label') / 'Select you type of usage',
                            L.select('.form-control', name='org') / (
                                L.option(value='individual', selected='') / 'Individual',
                                L.option(value='univ') / 'University',
                                L.option(value='pro') / 'Company',
                            )
                        ),
                        L.div('.form-group.text-center') / (
                            L.button('.btn.btn-primary', type='submit') / 'Continue'
                        )
                    ),
                ),
            ),
            FOOTER,
            SENTRY,
        ),
    )
)


def landing(request, articles):
    return base((
        L.div('.container') / (
            header(request),
            L.div('.row') / (
                L.div('.col-sm-12') / (
                    (
                        L.div('.alert.alert-success') / str(message),
                    ) for message in get_messages(request)
                ),
            ),
            L.div('.row') / (
                L.div('.col-sm-12') / (
                    L.div('#_graph-landing'),
                ),
            ),
            L.div('.row') / (
                L.div(style="margin: auto;max-width: 700px;font-size: 18px;") / (
                    L.h2 / "Innovative and efficient cluster analysis of networks with textual edges",
                    L.p / ("""
Linkage allows you to cluster the nodes of networks with textual edges while identifying topics which are used in communications. You can analyze with Linkage networks such as email networks or co-authorship networks. Linkage allows you to upload your own network data or to make requests on scientific databases (Arxiv, Pubmed, HAL).
"""
                    ),
                    L.div('text-center') / (
                        L.a('.btn.btn-primary.btn-lg', href='/jobs/add/') / 'Try Linkage',
                    ),
                    L.br,
                ),
            ),
            L.div('.row') / (
                L.hr,
                L.div('col-sm-12') / (
                    L.div(style='font-size: 1.3em;margin:auto;max-width:50%') / (
                        L.h4(style='color:#e95420') / (
                            icon('folder-open'),
                            SHORT_SPACER,
                            'Blog posts',
                        ),
                        L.div('.list-group') / (
                            (
                                L.div('.list-group-item') / (
                                    L.div('.list-group-item-heading') / (
                                        L.small(style='color:#ccc;float:right') / naturalday(article.published_on),
                                        L.a(href='/blog/' + article.slug + '/') / article.title,
                                    ),
                                ),
                            ) for article in articles
                        ),
                    ),
                    ),
          #       L.div('.col-sm-6') / (
          #           raw("""            <a class="twitter-timeline"  href="https://twitter.com/search?q=%22linkage.fr%22" data-widget-id="881809913659478017">Tweets about "linkage.fr"</a>
          #   <script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+"://platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script>
          # """)
          #       )
            ) if not settings.LINKAGE_ENTERPRISE else '',
            L.hr,
            L.div('.row') / (
                L.div('.col-sm-6') / (
                    L.h4(style='color:#e95420') / (
                        icon('certificate'),
                        SHORT_SPACER,
                        'How does Linkage work ?'
                    ),
                    L.p / """Linkage is built upon a sound statistical model for networks with textual edges and implement an innovative  and efficient inference algorithm to fit the model on your data. Model selection allows to find in a fully automatic way the best number of groups and topics."""
                ),
                L.div('.col-sm-6') / (
                    L.h4(style='color:#e95420') / (
                        icon('upload'),
                        SHORT_SPACER,
                        'Upload and manage your data securely',
                    ),
                    L.p / """Upload all or part of your data on the platform to analyze them with Linkage. You will keep full control on the data you upload and only you will be able to access them."""
                ),
            ),
            L.div('.row') / (
                L.div('.col-sm-6') / (
                    L.h4(style='color:#e95420') / (
                        icon('thumbs-up'),
                        SHORT_SPACER,
                        'Focus on data and interpretation',
                    ),
                    L.p / """Minimum configuration is required to use Linkage since it selects the most sensible parameters for the data you provide. No scientific background is required to start working and get results. Advanced configuration options are also available if you need specific setups."""
                ),
                L.div('.col-sm-6') / (
                    L.h4(style='color:#e95420') / (
                        icon('download'),
                        SHORT_SPACER,
                        'Visualize and export the results',
                    ),
                    L.p / """Linkage also provides advanced visualization tools, based on the specific features of the statistical modeling. Linkage finally allows to export as CSV files the clustering results obtained on your data for further processing."""
                ),
            ),
            L.div('.row') / (
                L.div('.col-sm-6') / (
                    L.h4(style='color:#e95420') / (
                        icon('education'),
                        SHORT_SPACER,
                        'The statistical method behind the platform',
                    ),
                    L.p / (
                        """The methodology implemented is partly related to an article published in the journal « Statistics and Computing ». The reference to cite in case of academic use of the platform is """,
                        L.a(href='https://arxiv.org/abs/1610.02427v2') / """« C. Bouveyron, P. Latouche and R. Zreik, The Stochastic Topic Block Model for the Clustering of Networks with Textual Edges, Statistics and Computing, in press, 2017. DOI: 10.1007/s11222-016-9713-7 ».""",
                    )
                ),
                L.div('.col-sm-6') / (
                    L.h4(style='color:#e95420') / (
                        icon('user'),
                        SHORT_SPACER,
                        'The people behind',
                    ),
                    L.p / """Linkage is developed by an academic team: """,
                    L.ul / (
                        L.li / (
                            'Methodology and code: ',
                            L.a(href='http://math.unice.fr/~cbouveyr/') / 'C. Bouveyron',
                            ' and ',
                            L.a(href='http://samm.univ-paris1.fr/Pierre-Latouche') / 'P. Latouche',
                        ),
                        L.li / (
                            'Web interface and visualizations: ',
                            L.a(href='http://dam.io') / 'D. Marié',
                        )
                    )
                ),
            ),
            FOOTER,
        ),
        JS_LIBS,
        L.script(src='/static/js/vendor/sigma.min.js'),
        L.script(src='/static/js/dist/vendor.js?v=' + COMMIT_HASH),
        L.script(src='/static/js/dist/landing.js?v=' + COMMIT_HASH),
    ))


def details(request, graph, results):
    return base((
        L.div('.container') / (
            header(request),
            L.div('.row') / (
                L.h3 / 'Details',
                L.code / graph.name,
                L.h4 / 'Results',
                L.table('.table') / (
                    L.thead / (
                        L.tr / (
                            L.th / 'topics Q',
                            L.th / 'clusters K',
                            L.th / 'crit',
                            L.th / 'clusters result',
                        ),
                    ),
                    L.tbody / (
                        (
                            (
                                L.tr / (
                                    L.td / str(result.param_topics),
                                    L.td / str(result.param_clusters),
                                    L.td / str(result.crit),
                                    L.td / result.clusters_mat,
                                )
                            )
                        ) for result in results
                    ),
                ),
                L.h4 / 'Log',
                L.pre / graph.job_log,
            ),
            FOOTER,
        ),
        SENTRY,
    ))


def terms(request):
    return base((
        L.div('.container') / (
            header(request),
            L.div('.row') / (
                L.div('.col-sm-12') / (
                    L.h3 / (
                        'Terms and conditions',
                        ' for Enterprise' if settings.LINKAGE_ENTERPRISE else '',
                    ),
                    L.ul / (
                        L.li / (
                            L.a(href='/static/doc/linkage-academic-terms.pdf') / 'For Academics',
                        ),
                        L.li / (
                            L.a(href='/static/doc/linkage-individual-terms.pdf') / 'For Individuals',
                        ),
                        L.li / (
                            L.a(href='/static/doc/linkage-private-terms.pdf') / 'For Private Partners',
                        ),
                    ),
                ),
            ),
            FOOTER,
            SENTRY,
        ),
    ))


def credits(request):
    return base((
        L.div('.container') / (
            header(request),
            L.div('.row') / (
                L.div('.col-sm-12') / (
                    L.h3 / 'Credits',
                    L.p / 'Linkage.fr is made of many open-source librairies that makes it possible, here\'s a few of them that we particularly thankful:',
                    L.ul / (
                        L.li / (
                            'sigma.js for the homepage animation',
                        ),
                        L.li / (
                            'Vivagraph for the interactive graphs',
                        ),
                        L.li / (
                            'Django for the web framework',
                        ),
                        L.li / (
                            'Celery & redis for the job runner',
                        ),
                        L.li / (
                            '(coming soon: the source code so you can see all the tools we used)',
                        ),
                    ),
                ),
            ),
            FOOTER,
            SENTRY,
        ),
    ))


def jobs(request, graphs, demo_graphs):
    return base((
        L.div('.container') / (
            header(request, 'jobs'),
            L.div('.row') / (
                (
                    L.div('#_jobs.col-sm-12') / (
                        L.h3('#_loading.text-center') / 'Loading…',
                    ),
                ) if len(graphs) > 0 else (
                    L.div('.alert.alert-warning') / 'No jobs yet'
                ),
            ),
            L.div('.row') / (
                L.div('.col-sm-12.hide_while_loading.hide') / (
                    L.hr,
                    L.h4 / 'Public jobs you can explore',
                    L.div('#_jobs_demo'),
                )
            ) if len(demo_graphs) > 0 else None,
            FOOTER
        ),
        JS_LIBS,
        L.script / raw("var USER_ID = %d;" % request.user.pk),
        L.script / raw("var JOBS = {};".format(json.dumps(
            api_jobs(graphs, demo_graphs),
        ))),
        L.script(src='/static/js/dist/vendor.js?v=' + COMMIT_HASH),
        L.script(src='/static/js/dist/jobs.js?v=' + COMMIT_HASH),
    ))


def api_jobs(graphs, demo_graphs):
    return {
        'user': [serialize_graph(g, None, simple=True) for g in graphs],
        'demo': [serialize_graph(g, None, simple=True) for g in demo_graphs],
    }


def tpl_article(request, article):
    return base((
        L.div('.container') / (
            header(request, 'blog'),
            L.div('.row') / (
                L.article('blog-article', style="""
    font-size: 1.3em;
    max-width: 800px;
    margin: auto;
    padding: 0 20px;
    border-right: 1px solid #d2d2d2;
    border-left: 1px solid #d2d2d2;
""") / (
                    L.h2(style="""
    margin-bottom: 50px;
    border-bottom: 9px solid #e95420;
    padding-bottom: 20px;
    background: whitesmoke;
    padding: 20px 10px;
    margin-top: 0;
                        """) / (
                        L.a('text-muted', href='/', style="""
                            display: block;
    margin-bottom: 10px;
    font-size: 18px;""") / 'Blog',
                        article.title
                    ),
                    L.p / raw(mistune.markdown(article.content, escape=False)),
                    L.small('text-muted') / (
                        'Published ', naturalday(article.published_on),
                    ),
                ),
            ),
            FOOTER
        ),
        SENTRY,
    ), title=article.title)


def error(request, code, msg):
    return base((
        L.div('.container') / (
            L.style / 'body{background: none}',
            L.div('.row') / (
                L.div('.col-sm-12.text-center', style='padding:100px') / (
                    L.hr,
                    L.h1 / str(code),
                    L.h3 / msg,
                    L.a(href='/') / 'back to linkage.fr',
                    L.hr,
                ),
            ),
        ),
    ), title=msg)
