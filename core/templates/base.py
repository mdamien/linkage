from lys import L, render, raw

CSS = L.style / raw("""
/* hack for bootstrap + vivagraph */
#_graph > svg, #_loading { width: 100%; height: 700px }
#_loading { padding: 200px; color: #888 }
/* hack for bootstrap + firefox + input[file] */
.form-control {
    height: auto;
}
body { background: #eee }
.container { background: white; margin-top: 10px; border-radius: 4px }
.container-fluid { background: white; margin: 10px; border-radius: 4px }
.histogram > span {
    background: #3a87ad;
    height: 20%;
    display: inline-block;
    width: 30px;
    margin-top: auto;
}

.histogram {
    height: 50px;
    display: flex;
}

.blog-article img {
    box-shadow: 0 0 48px #8a8a8a;
    max-width: 50%;
    display: block;
    margin: auto;
    margin-top: 50px;
    margin-bottom: 50px;
}
""".replace('\n', ' '))

def basic_frame(*content, title=''):
    return render((
        raw('<!DOCTYPE html>'),
        L.html / (
            L.head / (
                L.meta(charset='utf-8'),
                L.title / (((title + ' - ') if title else '') + 'Linkage'),
                L.link(rel='icon', type='image/png', href='/static/img/favicon.png'),
                L.link(rel='stylesheet', href="/static/css/bootstrap.css"),
                L.link(rel='stylesheet', href="/static/css/balloon.css"),
                L.link(rel='stylesheet', href="/static/css/rc-slider.css"),
                CSS,
            ),
            L.body / content,
        ),
    ))

def base(*content, **kwargs):
    return basic_frame(content, **kwargs)
