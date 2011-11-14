from tech.models import Post, LikeWordCount, DislikeWordCount
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.core import serializers

import re

def index (request):
    return render_to_response('index.html')

def posts (request):
    data = serializers.serialize('json', Post.objects.filter(like=None).order_by('-rating'), ensure_ascii=False, fields=('source', 'title', 'link', 'date', 'rating'))
    return HttpResponse(data)

def like (request, pk):
    if request.method != 'PUT':
        return HttpResponseBadRequest()

    post = Post.objects.get(pk=pk)
    for word in re.findall(r"[a-zA-Z0-9_\.\+]+",post.title):
        word = word.strip().lower()
        wc = LikeWordCount.objects.filter(word=word)
        if len(wc) == 0:
            LikeWordCount(word=word,count=1).save()
        else:
            wc = wc[0]
            wc.count += 1
            wc.save()
    post.like = True
    post.save()

    return HttpResponse("liked %s (%s)" % (pk,post.title) )

def dislike (request, pk):
    if request.method != 'PUT':
        return HttpResponseBadRequest()

    post = Post.objects.get(pk=pk)
    for word in re.findall(r"[a-zA-Z0-9_\.\+]+",post.title):
        word = word.strip().lower()
        wc = DislikeWordCount.objects.filter(word=word)
        if len(wc) == 0:
            DislikeWordCount(word=word,count=1).save()
        else:
            wc = wc[0]
            wc.count += 1
            wc.save()
    post.like = False
    post.save()

    return HttpResponse("disliked %s (%s)" % (pk,post.title) )
