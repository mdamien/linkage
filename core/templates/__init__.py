from lys import L, raw

from .base import base

TITLEBAR = L.div('.row') / (
    L.div('.col-md-12') / (
        L.nav('.navbar.navbar-default') / (
            L.div('.navbar-header') / (
                L.a('.navbar-brand', href='#') / 'Linkage',
            )
        )
    )
)

def result(**args):
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
        L.script / raw("""
          var graphGenerator = Viva.Graph.generator();
          var graph = graphGenerator.wattsStrogatz(150, 4, 0.2);

          var layout = Viva.Graph.Layout.forceDirected(graph, {
              springLength : 10,
              springCoeff : 0.0005,
              dragCoeff : 0.02,
              gravity : -1.2
          });

          var renderer = Viva.Graph.View.renderer(graph, {
              container: document.getElementById('graph'),
              layout: layout,
          });
          renderer.run();
        """)
    ))

def index(**args):
    return base((
        L.br,
        L.div('.container-fluid') / (
            TITLEBAR,
            L.div('.row') / (
                L.div('.col-md-12') / (
                    L.p / (
                        L.h3 / 'Make a graph',
                        L.ul / (
                            L.a('.btn.btn-primary.btn-large', href='#') / 'Gmail import', ' ',
                            L.a('.btn.btn-primary.btn-large', href='#') / 'arXiv topic', ' ',
                            L.a('.btn.btn-primary.btn-large', href='#') / 'PubMed topic',
                        ),
                        L.h3 / 'Upload your own graph',
                        L.form('.row') / (
                            L.div('.col-md-5') / L.input('form-control', type='file'),
                            L.div('.col-md-3') / (
                                L.a('.btn.btn-primary.btn-large', href='#') / 'Import',
                            ),
                        )
                    ),
                    L.hr,
                    L.h1 / 'Uploaded graphs',
                    L.ul / (
                        L.li / (
                            L.a(href='/result/', style='color:grey') /
                                '\'GMail import\' one hour ago (processing 40%)'
                        ),
                        L.li / (
                            L.a(href='/result/') /
                                '\'GMail import\' on Feb 5, 2017'
                        ),
                        L.li / (
                            L.a(href='/result/') /
                                '\'GMail import\' on Feb 2, 2017'
                        ),
                        L.li / (
                            L.a(href='/result/') /
                                '\'archiv search for "statistics"\' on Feb 1, 2017'
                        ),
                    ),
                ),
            ),
        ),
    ))
