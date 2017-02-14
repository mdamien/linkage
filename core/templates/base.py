from lys import L, render, raw

CSS = L.style / raw("""
/* hack for bootstrap + vivagraph */
#_graph > svg { width: 100%; height: 700px }
/* hack for bootstrap + firefox + input[file] */
.form-control {
    height: auto;
}
""")

def basic_frame(*content):
    return render((
        raw('<!DOCTYPE html>'),
        L.html / (
            L.head / (
                L.meta(charset='utf-8'),
                L.title / 'Linkage',
                L.link(rel='icon', type='image/png', href='/static/img/favicon.png'),
                L.link(rel='stylesheet', href="/static/css/bootstrap.css", crossorigin="anonymous"),
                CSS,
            ),
            L.body / content,
        ),
    ))

def base(*content, **kwargs):
    return basic_frame(content, **kwargs)
