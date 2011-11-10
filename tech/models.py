from django.db import models

class Post (models.Model):
    source = models.CharField(max_length=128)
    title  = models.CharField(max_length=1024)
    link   = models.CharField(max_length=1024, unique=True)
    date   = models.DateField()
    desc   = models.TextField()
    rating = models.PositiveIntegerField(default=0)
    like   = models.NullBooleanField(default=None)
    def __unicode__ (self):
        return unicode(self.source) + unicode(": ") + unicode(self.title)

class LikeWordCount (models.Model):
    word  = models.CharField(max_length=256, unique=True)
    count = models.PositiveIntegerField(default=0)
    def __unicode__ (self):
        return unicode(self.word) + unicode(": ") + unicode(self.count)

class DislikeWordCount (models.Model):
    word  = models.CharField(max_length=256, unique=True)
    count = models.PositiveIntegerField(default=0)
    def __unicode__ (self):
        return unicode(self.word) + unicode(": ") + unicode(self.count)
