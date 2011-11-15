from django.core.management.base import BaseCommand
from tech.models import Post

class Command(BaseCommand):
    help = 'Prints posts database'

    def handle (self, *args, **options):
        for post in Post.objects.filter(like=None).order_by('-rating'):
            self.stdout.write(str(post) + "\n")
