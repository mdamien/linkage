import os

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from .models import Article
from core.templates import article as article_template

def article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    return HttpResponse(article_template(request, article))
