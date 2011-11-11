from tech.models import Post, LikeWordCount, DislikeWordCount
from django.shortcuts import render_to_response

def index (request):
    return render_to_response('index.html', {
        'posts'    : Post.objects.all().order_by('-rating'),
        'likes'    : LikeWordCount.objects.all().order_by('-count'),
        'dislikes' : DislikeWordCount.objects.all().order_by('-count'),
        })
