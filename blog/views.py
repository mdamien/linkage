import os

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from .models import Article
from core.templates import tpl_article


def article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    return HttpResponse(tpl_article(request, article))
