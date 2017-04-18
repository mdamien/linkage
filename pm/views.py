import os

from django.shortcuts import render

from django.http import HttpResponse, JsonResponse


def manifest(requests, pk):
    return JsonResponse({
        'all': ['data'],
        'last': 'data',
    })

def labels(requests, pk):
    pk = int(pk)
    return HttpResponse(open('pm_runs/%d/out/labels.json' % (pk), 'rb'))

def links(requests, pk):
    pk = int(pk)
    return HttpResponse(open('pm_runs/%d/out/links.bin' % (pk), 'rb'))

def meta(requests, pk):
    pk = int(pk)
    return HttpResponse(open('pm_runs/%d/out/meta.json' % (pk), 'rb'))

def positions(requests, pk):
    pk = int(pk)
    best = max((int(f.split('.')[0]) for f in os.listdir('pm_runs/%d/layout/' % pk)))
    return HttpResponse(open('pm_runs/%d/layout/%d.bin' % (pk, best), 'rb'))
