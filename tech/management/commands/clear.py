from django.core.management.base import BaseCommand
from tech.models import Post

class Command(BaseCommand):
    help = 'Clear posts database'

    def handle (self, *args, **options):
        for post in Post.objects.all():
            post.delete()
