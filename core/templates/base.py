from lys import L, render, raw
from django.conf import settings


def basic_frame(*content, title=''):
    return render((
        raw('<!DOCTYPE html>'),
        L.html / (
            L.head / (
                L.meta(charset='utf-8'),
                L.title / (((title + ' - ') if title else '') + 'Linkage' + (' Enterprise' if settings.LINKAGE_ENTERPRISE else '')),
                L.link(rel='icon', type='image/png', href='/static/img/favicon.png'),
                L.link(rel='stylesheet', href="/static/css/bootstrap.css"),
                L.link(rel='stylesheet', href="/static/css/balloon.css"),
                L.link(rel='stylesheet', href="/static/css/rc-slider.css"),
                L.link(rel='stylesheet', href="/static/css/base.css"),
                L.script / raw("var LINKAGE_ENTERPRISE = %s;" % ('true' if settings.LINKAGE_ENTERPRISE else 'false')),
            ),
            L.body / content,
        ),
    ))


def base(*content, **kwargs):
    return basic_frame(content, **kwargs)
