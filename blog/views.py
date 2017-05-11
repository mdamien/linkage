import os

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from .models import Article

def article(requests, slug):
    article = get_object_or_404(Article, slug=slug)
    return HttpResponse(article.title + '\n<br/>' + article.content)
