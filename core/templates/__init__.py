import collections, csv, json

from django.middleware.csrf import get_token
from django.contrib.humanize.templatetags.humanize import naturaltime

from lys import L, raw

from .base import base

def header(request):
    return L.div('.row') / (
        L.div('.col-md-6') / (
            L.a(href='/') / (L.h2 / 'Linkage'),
        ),
        L.div('.col-md-6.text-right') / (
            L.a('.btn.btn-link', href='/admin/', style='margin-top: 20px;display:inline-block') / 'admin',
            L.a('.btn.btn-link', href='/accounts/logout/', style='margin-top: 20px;display:inline-block') / 'logout',
        ) if request.user.is_authenticated else None,
    ), L.hr

SPACER = raw('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;') # dat spacer
FOOTER = L.div('.row') / (
    L.div('.col-md-12 text-center') / (
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
        L.a(href='http://univ-paris1.fr/') / L.img(src='/static/img/paris1.png', height='60'),
    ),
)

JS_LIBS = (
        L.script(src='/static/js/vendor/jquery.js'),
        L.script(src='/static/js/vendor/tether.js'),
        L.script(src='/static/js/vendor/bootstrap.js'),
)

def serialize_graph(graph, result):
    data = {
        'name': graph.name,
        'links': graph.links,
        'created_at': naturaltime(graph.created_at),
    }
    if result:
        data['result'] = {
            'progress': result.progress,
            'clusters': result.clusters,
            'topics': result.topics,
            'topics_terms': result.topics_terms,
        }
    return json.dumps(data)

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
                        L.div('#_graph.panel-body'),
                    )
                ),
            ),
        ),
        JS_LIBS,
        L.script(src='/static/js/vendor/vivagraph.js'),
        L.script(src='/static/js/vendor/papaparse.js'),
        L.script / raw("var GRAPH = {}".format(serialize_graph(graph, result))),
        L.script(src='/static/js/dist/vendor.js'),
        L.script(src='/static/js/dist/graph.js'),
    ))


def index(request, graphs):
    return base((
        L.div('.container') / (
            header(request),
            L.div('.row') / (
                L.div('.col-md-6') / (
                    L.form('.row.form-horizontal', method="post", enctype="multipart/form-data") / (
                        L.input(type='hidden', name='csrfmiddlewaretoken', value=get_token(request)),
                        L.input(type='hidden', name='action', value='import'),
                        L.p / (
                            L.h4 / 'Import a graph via an arXiv request',
                            L.div('.row') / (
                                L.div('.col-md-9') / L.input('.form-control', type='text', name='q'),
                                L.div('.col-md-3') / (
                                    L.input('.btn.btn-primary.btn-large', name='choice_arxiv', type='submit', value='search'),
                                )
                            ),
                            L.h4 / 'Or via a file',
                            L.div('.row') / (
                                L.div('.col-md-5') / L.input('form-control', type='file', name='csv_file'),
                                L.div('.col-md-6') / (
                                    L.input('.btn.btn-primary.btn-large', name='choice_csv', type='submit', value='Import .csv'),
                                    SPACER,
                                    L.input('.btn.btn-primary.btn-large', name='choice_mbox', type='submit', value='Import .mbox'),
                                )
                            ),
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
                            L.div('.form-group._clustering-options') / (
                                L.div('.col-md-3.control-label') / (L.strong / 'Clusters (Q)'),
                                L.div('.col-md-9') / (
                                    L.input(name='clusters', value='10', type='number'),
                                ),
                            ),
                            L.div('.form-group._clustering-options') / (
                                L.div('.col-md-3.control-label') / (L.strong / 'Topics (K)'),
                                L.div('.col-md-9') / (
                                    L.input(name='topics', value='10', type='number'),
                                ),
                            ),
                        )
                    )
                ),
                (
                    L.div('.col-md-6') / (
                        L.h4 / 'Uploaded graphs',
                        L.div('.list-group') / (
                            L.a('.list-group-item', href=graph.get_absolute_url()) / (
                                L.div('.row') / (
                                    L.div('.col-md-10') / (
                                        str(graph)
                                    ),
                                    L.div('.col-md-2') / (
                                        L.form(method='post') / (
                                            L.input(type='hidden', name='csrfmiddlewaretoken', value=get_token(request)),
                                            L.input(type='hidden', name='action', value='delete'),
                                            L.input(type='hidden', name='graph_id', value=str(graph.pk)),
                                            L.button('.btn.btn-primary.btn-xs', type='submit') / 'delete', # L.span('.glyphicon.glyphicon-remove'),
                                        )
                                    )
                                )
                                
                            ) for graph in graphs),
                    ),
                ) if len(graphs) > 0 else None,
            ),
            FOOTER
        ),
        JS_LIBS,
        L.script(src='/static/js/src/import.js'),
    ))


def login(request):
    return base((
        L.div('.container') / (
            header(request),
            L.div('.row') / (
                L.div('.col-md-3.center-block', style='float:none') / (
                    L.div('.alert.alert-dismissible.alert-info') / 'You need to login to access this application',
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
                ),
            ),
            FOOTER
        ),
    ))
