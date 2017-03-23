import random, collections, csv, json, io, sys, os

from django.middleware.csrf import get_token
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.conf import settings

from lys import L, raw

from .base import base

csv.field_size_limit(sys.maxsize) # http://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072
DEBUG = settings.DEBUG
COMMIT_HASH = settings.COMMIT_HASH

SPACER = raw('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;') # dat spacer
SHORT_SPACER = raw('&nbsp;&nbsp;')

def header(request, page_name=''):
    return L.div('.row') / (
        L.div('.col-md-2') / (
            L.a(href='/') / (
                L.h2 / ('Linkage' + ('*' if DEBUG else None)),
            ),
        ),
        L.div('.col-md-5') / (
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
        L.div('.col-md-5.text-right') / (
            (
                L.a('.btn.btn-link', href='/admin/', style='margin-top: 20px;display:inline-block') / 'admin'
            ) if request.user.is_staff else None,
            L.a('.btn.btn-link', href='/accounts/logout/', style='margin-top: 20px;display:inline-block') / 'logout',
        ) if request.user.is_authenticated else None,
    ), L.hr

FOOTER = (
    L.div('.row') / (
        L.div('.col-md-12 text-center') / (
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
                L.a(href='/about/terms/') / 'Privacy Policy',
                SPACER,
                L.a(href='/about/terms/') / 'Terms and conditions',
            ),
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

def serialize_graph(graph, result, simple=False):
    data = {
        'id': graph.pk,
        'name': graph.name,
        'labels': graph.labels,
        'edges': graph.edges,
        'tdm': graph.tdm,
        'dictionnary': graph.dictionnary,
        'directed': graph.directed,
        'created_at': naturaltime(graph.created_at),
        'url': graph.get_absolute_url(),
        'log': graph.job_log,
        'time': graph.job_time,
        'progress': graph.job_progress,
        'job_param_clusters': graph.job_param_clusters,
        'job_param_topics': graph.job_param_topics,
        'job_param_clusters_max': graph.job_param_clusters_max,
        'job_param_topics_max': graph.job_param_topics_max,
    }
    if simple:
        del data['tdm']
        del data['dictionnary']
        del data['labels']
        del data['edges']
    if result:
        data['result'] = result.serialize()
    return data

def result(request, graph, result):
    return base((
        L.div('.container-fluid') / (
            header(request),
            L.div('.row') / (
                L.div('.col-md-3') / (
                    L.div('#_sidebar'),
                ),
                L.div('.col-md-9') / (
                    L.div('.panel.panel-default', style='position:relative') / (
                        L.div('#_graph-sidebar'),
                        L.div('#_graph.panel-body') / (
                            L.h3('#_loading.text-center') / 'Loading…'
                        ),
                    )
                ),
            ),
            FOOTER,
        ),
        JS_LIBS,
        L.script(src='/static/js/vendor/vivagraph.js'),
        L.script(src='/static/js/vendor/papaparse.js'),
        L.script / raw("var GRAPH = {};".format(json.dumps(serialize_graph(graph, result)))),
        L.script(src='/static/js/dist/vendor.js?v=' + COMMIT_HASH),
        L.script(src='/static/js/dist/graph.js?v=' + COMMIT_HASH),
    ), title=graph.name)


def api_result(request, graph, result):
    return serialize_graph(graph, result)


def index(request, messages, import_type_selected='coauth'):
    if not import_type_selected:
        import_type_selected = 'coauth'
    return base((
        L.div('.container') / (
            header(request, 'addjob'),
            L.div('.row') / (
                L.div('.col-md-12') / (
                    L.h4 / 'Import',
                ),
            ),
            L.div('.row') / (
                L.div('.col-md-3') / (
                    L.div('.list-group') / (
                        L.a('.list-group-item' + ('.active' if import_type_selected == 'coauth' else ''),
                            href='?import_type=coauth') / 'Co-authorship network',
                        L.a('.list-group-item' + ('.active' if import_type_selected == 'mbox' else ''),
                            href='?import_type=mbox') / 'MBox',
                        L.a('.list-group-item' + ('.active' if import_type_selected == 'csv' else ''),
                            href='?import_type=csv') / 'CSV',
                        L.a('.list-group-item' + ('.active' if import_type_selected == 'sample' else ''),
                            href='?import_type=sample') / 'Sample',
                    ),
                ),
                L.div('.col-md-9') / (
                    (L.div('.alert.alert-' + msgtype) / msg for msgtype, msg in messages),
                    L.form('.row.form-horizontal', method="post", enctype="multipart/form-data") / (
                        L.input(type='hidden', name='csrfmiddlewaretoken', value=get_token(request)),
                        L.input(type='hidden', name='action', value='import'),
                        (
                            L.div('.row') / (
                                L.div('.col-md-5') / L.input('.form-control', type='text', name='q', placeholder="'security', 'defense', 'weapons', 'deep learning',.."),
                                L.div('.col-md-7') / (
                                    L.input('.btn.btn-primary.btn-large', name='choice_arxiv', type='submit', value='search arXiv'),
                                    SPACER,
                                    L.input('.btn.btn-primary.btn-large', name='choice_hal', type='submit', value='search HAL'),
                                )
                            ),
                        ) if import_type_selected == 'coauth' else None,
                        (
                            L.div('.row') / (
                                L.div('.col-md-7') / L.input('form-control', type='file', name='csv_file'),
                                L.div('.col-md-5') / (
                                    L.input('.btn.btn-primary.btn-large',
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
                                L.div('.col-md-7') / L.input('form-control', type='file', name='mbox_file'),
                                L.div('.col-md-5') / (
                                    L.input('.btn.btn-primary.btn-large', name='choice_mbox', type='submit', value='Import .mbox'),
                                )
                            ),
                            L.div('.form-group._mbox-options') / (
                                L.div('.col-md-3.control-label') / (' '),
                                L.div('.col-md-9') / (
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
                                L.div('.col-md-7') / (
                                    L.select('.form-control', name='sample_dropdown') / (
                                        (
                                            L.option(value=filename) / filename
                                        ) for filename in sorted(os.listdir('csv_samples/'))
                                    )
                                ),
                                L.div('.col-md-5') / (
                                    L.input('.btn.btn-primary.btn-large', name='choice_dropdown', type='submit', value='Import'),
                                )
                            ),
                        ) if import_type_selected == 'sample' else None,
                        L.hr,
                        L.div('.form-group') / (
                            L.div('.col-md-3.control-label') / (L.strong / 'Clustering'),
                            L.div('.col-md-9') / (
                                L.div('.radio') / (
                                    L.label / (
                                        L.input(name='clustering', value='auto', checked='', type='radio'), 'Auto',
                                    ),
                                ),
                                L.div('.radio') / (
                                    L.label / (
                                        L.input(name='clustering', value='manual', type='radio'), 'Manual',
                                    ),
                                )
                            ),
                        ),
                        L.div('.form-group._clustering-options.hide') / (
                            L.div('.col-md-3.control-label') / (L.strong / 'Clusters (Q)'),
                            L.div('.col-md-9') / (
                                L.input(name='clusters', value='10', type='number'),
                            ),
                        ),
                        L.div('.form-group._clustering-options.hide') / (
                            L.div('.col-md-3.control-label') / (L.strong / 'Topics (K)'),
                            L.div('.col-md-9') / (
                                L.input(name='topics', value='10', type='number'),
                            ),
                        ),
                    )
                ),
            ),
            FOOTER
        ),
        JS_LIBS,
        L.script(src='/static/js/src/import.js?v=' + COMMIT_HASH),
    ))

def login(request, message):
    return base((
        L.div('.container') / (
            header(request),
            L.div('.row') / (
                L.div('.col-md-3.center-block', style='float:none') / (
                    (L.div('.alert.alert-danger') / message) if message else (
                        L.div('.alert.alert-info') / 'You need to login to access this application'
                    ),
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
                        )
                    ),
                    L.p / (
                        'No account yet ? you can ',
                        L.a(href='/accounts/signup/') / 'sign up here',
                    )
                ),
            ),
            FOOTER,
            SENTRY,
        ),
    ))


def landing(request):
    return base((
        L.div('.container') / (
            header(request),
            L.div('.row') / (
                L.div('.col-md-3.center-block.text-center', style='float:none') / (
                    L.p / (
                        'Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet.'
                    ),
                    L.a('.btn.btn-primary.btn-large', href='/jobs/add/') / 'Try Linkage'
                ),
            ),
            FOOTER,
        ),
        SENTRY,
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
                )
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
                L.div('.col-md-12') / (
                    L.h3 / 'Terms and conditions',
                    L.p / (
                        'Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet.'
                    ),
                    L.p / (
                        'Lorem. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet.'
                    ),
                    L.p / (
                        'Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet.'
                    ),
                    L.p / (
                        'Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet. Lorem ipsum dolor asimet it fet.'
                    ),
                ),
            ),
            FOOTER,
            SENTRY,
        ),
    ))


def jobs(request, graphs):
    return base((
        L.div('.container') / (
            header(request, 'jobs'),
            L.div('.row') / (
                (
                    L.div('#_jobs.col-md-12') / 'loading…',
                ) if len(graphs) > 0 else (
                    L.div('.alert.alert-warning') / 'No jobs yet'
                ),
            ),
            FOOTER
        ),
        JS_LIBS,
        L.script / raw("var USER_ID = %d;" % (request.user.pk,)),
        L.script / raw("var JOBS = {};".format(json.dumps(
            [serialize_graph(g, None, simple=True) for g in graphs]
        ))),
        L.script(src='/static/js/dist/vendor.js?v=' + COMMIT_HASH),
        L.script(src='/static/js/dist/jobs.js?v=' + COMMIT_HASH),
    ))

def api_jobs(graphs):
    return [serialize_graph(g, None, simple=True) for g in graphs]
