import os

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from .models import Article
from core.templates import tpl_article, tpl_article_list

def article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    return HttpResponse(tpl_article(request, article))

def article_list(request):
    return HttpResponse(tpl_article_list(request, Article.objects.all().order_by('-pk').filter(published=True)))
