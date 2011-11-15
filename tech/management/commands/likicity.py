from django.core.management.base import BaseCommand
from django.core import serializers
from tech.models import LikeWordCount, DislikeWordCount
import json

class Command(BaseCommand):
    help = 'Prints likicity of each word'

    def handle (self, *args, **options):
        likes = {}
        for like in LikeWordCount.objects.all():
            likes[like.word] = float(like.count)

        dislikes = {}
        for dislike in DislikeWordCount.objects.all():
            dislikes[dislike.word] = float(dislike.count)

        for word in likes.keys():
            if not word in dislikes:
                dislikes[word] = float(0)
        for word in dislikes.keys():
            if not word in likes:
                likes[word] = float(0)

        likicity = {}
        for word in likes.keys():
            l = likes[word]
            d = dislikes[word]
            likicity[word] = int((l / (d + l)) * 100)
        for word in dislikes.keys():
            l = likes[word]
            d = dislikes[word]
            likicity[word] = int((l / (d + l)) * 100)
        for word in likicity.keys():
            if likes[word] + dislikes[word] > 10:
                print likicity[word], int(likes[word] + dislikes[word]), word
