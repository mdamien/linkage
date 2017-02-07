from lys import L, render, raw

CSS = L.style / raw("""
/* hack for bootstrap + vivagraph */
#graph > svg { width: 100%; height: 700px }
""")

def basic_frame(*content):
    return render((
        raw('<!DOCTYPE html>'),
        L.html / (
            L.head / (
                L.meta(charset='utf-8'),
                L.title / 'Linkage',
                L.link(rel='stylesheet', href="https://bootswatch.com/united/bootstrap.css", crossorigin="anonymous"),
                CSS,
            ),
            L.body / content,
        ),
    ))

def base(*content, **kwargs):
    return basic_frame(content, **kwargs)
