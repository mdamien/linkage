import collections, csv
from io import StringIO

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

def _result_sidebar(graph, result):
    nodes = set()
    nb_links = 0
    for link in csv.reader(StringIO(graph.links), delimiter=','):
        if len(link) > 0:
            nodes.add(link[0])
            nodes.add(link[1])
            nb_links += 1

    clusters = collections.Counter([line.split(',')[-1] for line in result.clusters.split('\n') if line])
    topics = collections.Counter([line.split(',')[-1] for line in result.topics.split('\n') if line])

    return (
        L.div('.panel.panel-primary') / (
            L.div('.panel-heading') / (
                L.h3('.panel-title') / graph.name
            ),
            L.div('.panel-body') / (
                L.strong() / str(nb_links),' edges ',
                L.br,
                L.strong() / str(len(nodes)), ' nodes',
                L.br,
                'imported ', L.strong() / naturaltime(graph.created_at),
            )
        ),
        L.hr,
        L.div('.panel.panel-default') / (
            L.div('.panel-heading') / (
                L.h3('.panel-title') / (str(len(clusters)), ' clusters'),
            ),
            L.div('.list-group') / (
                (
                    L.div('.list-group-item') / ('%s (%d)' % (cluster, c))
                ) for cluster, c in clusters.most_common()
            ),
        ) if result else None,
        L.div('.panel.panel-default') / (
            L.div('.panel-heading') / (
                L.h3('.panel-title') / (str(len(topics)), ' topics'),
            ),
            L.div('.list-group') / (
                (
                    L.div('.list-group-item') / ('%s (%d)' % (topic, c))
                ) for topic, c in topics.most_common()
            ),
        ) if result else None,
    )

def result(request, graph, result):
    return base((
        L.div('.container-fluid') / (
            header(request),
            L.div('.row') / (
                L.div('.col-md-2') / (
                    _result_sidebar(graph, result)
                ),
                L.div('.col-md-10') / (
                    L.ul('.nav.nav-tabs') / (
                        L.li('.active') / (L.a(href='#network', data_toggle='tab') / 'Network'),
                        L.li / (L.a(href='#terms', data_toggle='tab') / 'Terms'),
                        L.li / (L.a(href='#groups', data_toggle='tab') / 'Groups connexions'),
                        L.li / (L.a(href='#topics', data_toggle='tab') / 'Topics connexions'),
                    ) if False else None,
                    L.div('#outputTabs.tab-content') / (
                        L.div('#network.tab-pane.active') / L.div('#graph'),
                        L.div('#terms.tab-pane') / 'terms',
                        L.div('#groups.tab-pane') / 'groups',
                        L.div('#topics.tab-pane') / 'topics',
                    ),
                ),
            ),
        ),
        L.script(src='/static/js/jquery.js'),
        L.script(src='/static/js/tether.js'),
        L.script(src='/static/js/bootstrap.js'),
        L.script(src='/static/js/vivagraph.js'),
        L.script(src='/static/js/papaparse.js'),
        L.script / raw("var GRAPH_ID = {}".format(graph.pk)),
        L.script(src='/static/js/graph.js'),
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
                            L.h4 / 'Import a graph for processing',
                            L.div('.row') / (
                                L.div('.col-md-9') / L.input('.form-control', type='text', name='q'),
                                L.div('.col-md-3') / (
                                    L.button('.btn.btn-primary.btn-large', href='#') / 'arXiv topic'
                                )
                            ),
                            L.br,
                            L.div('.row') / (
                                L.div('.col-md-9') / L.input('form-control', type='file', name='csv_file'),
                                L.div('.col-md-3') / (
                                    L.input('.btn.btn-primary.btn-large', href='#', type='submit', value='Import .csv'),
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
                            L.div('.form-group') / (
                                L.div('.col-md-3.control-label') / (L.strong / 'Clusters (Q)'),
                                L.div('.col-md-9') / (
                                    L.input(name='clusters', value='10', type='number'),
                                ),
                            ),
                            L.div('.form-group') / (
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
