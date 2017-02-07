from django.middleware.csrf import get_token

from lys import L, raw

from .base import base

TITLEBAR = L.div('.row') / (
    L.div('.col-md-12') / (
        L.nav('.navbar.navbar-default') / (
            L.div('.navbar-header') / (
                L.a('.navbar-brand', href='/') / 'Linkage',
            )
        )
    )
)

def result(request, graph):
    return base((
        L.br,
        L.div('.container-fluid') / (
            TITLEBAR,
            L.div('.row') / (
                L.div('.col-md-2') / (
                    L.div('.well') / (
                        L.strong / '4', ' groups', L.br, L.strong / '10', ' topics'
                    )
                ),
                L.div('.col-md-10') / (
                    L.ul('.nav.nav-tabs') / (
                        L.li('.active') / (L.a(href='#network', data_toggle='tab') / 'Network'),
                        L.li / (L.a(href='#terms', data_toggle='tab') / 'Terms'),
                        L.li / (L.a(href='#groups', data_toggle='tab') / 'Groups connexions'),
                        L.li / (L.a(href='#topics', data_toggle='tab') / 'Topics connexions'),
                    ),
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
        L.br,
        L.div('.container-fluid') / (
            TITLEBAR,
            L.div('.row') / (
                L.div('.col-md-12') / (
                    L.p / (
                        L.h3 / 'Make a graph',
                        L.form('.row', method='POST') / (
                            L.input(type='hidden', name='csrfmiddlewaretoken', value=get_token(request)),
                            L.div('.col-md-5') / L.input('.form-control', type='text', name='q'),
                            L.ul / (
                                L.button('.btn.btn-primary.btn-large', href='#') / 'arXiv topic', ' ',
                                L.a('.btn.btn-primary.btn-large', href='#') / 'PubMed topic',
                            ),
                        ),
                        L.a('.btn.btn-primary.btn-large', href='#') / 'Gmail import', ' ',
                        L.h3 / 'Upload your own graph',
                        L.form('.row', method="post", enctype="multipart/form-data") / (
                            L.input(type='hidden', name='csrfmiddlewaretoken', value=get_token(request)),
                            L.div('.col-md-5') / L.input('form-control', type='file', name='csv_file'),
                            L.div('.col-md-3') / (
                                L.input('.btn.btn-primary.btn-large', href='#', type='submit', value='Import'),
                            ),
                        )
                    ),
                    L.hr,
                    L.h1 / 'Uploaded graphs',
                    L.ul / (
                        L.li / (
                            L.a(href=graph.get_absolute_url()) / str(graph)
                        ) for graph in graphs),
                ),
            ),
        ),
    ))
