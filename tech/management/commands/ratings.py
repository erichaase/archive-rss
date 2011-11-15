from django.core.management.base import BaseCommand
from tech.models import Post, LikeWordCount, DislikeWordCount

import re

class Command(BaseCommand):
    help = 'Update post ratings'

    def handle (self, *args, **options):
        for post in Post.objects.all():
            rating = getRating(post.title)
            if rating != post.rating:
                post.rating = rating
                post.save()

# see http://en.wikipedia.org/wiki/Bayesian_spam_filtering#Mathematical_foundation for more details
def getRating (title):
    p = []
    for word in re.findall(r"[a-zA-Z0-9_\.\+]+", title.strip().lower()):
        lwc = LikeWordCount.objects.filter(word=word)
        if len(lwc) == 0:
            lwc = 0
        else:
            lwc = lwc[0].count
        lwc = float(lwc)

        dwc = DislikeWordCount.objects.filter(word=word)
        if len(dwc) == 0:
            dwc = 0
        else:
            dwc = dwc[0].count
        dwc = float(dwc)

        if lwc + dwc != 0:
            s = 3.0
            r = (s / 2 + lwc) / (s + lwc + dwc)
            p.append(r)

    if len(p) == 0:
        return 50

    a = 1.0
    b = 1.0
    for x in p:
        a *= x
        b *= (1.0 - x)
    if a + b == 0:
        return 50
    return int((a / (a + b) ) * 100)
