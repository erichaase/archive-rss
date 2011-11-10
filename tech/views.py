from __future__ import division

import urllib2
import xml.etree.ElementTree
import datetime
import re

from tech.models import Post, LikeWordCount, DislikeWordCount
from django.shortcuts import render_to_response

def index (request):
    update()
    return render_to_response('index.html', {
        'posts'    : Post.objects.all().order_by('-rating'),
        'likes'    : LikeWordCount.objects.all().order_by('-count'),
        'dislikes' : DislikeWordCount.objects.all(),
        })

def update():
    for x in Post.objects.all():
        x.delete()
    getPosts()

def getPosts():
    getSlashdot()

def getSlashdot():
    html = urllib2.urlopen('http://rss.slashdot.org/Slashdot/slashdot').read()
    rss = xml.etree.ElementTree.XML(html)
    #xml.etree.ElementTree.dump(rss)

    ns1 = 'http://purl.org/rss/1.0/'
    ns2 = 'http://rssnamespace.org/feedburner/ext/1.0'
    ns3 = 'http://purl.org/dc/elements/1.1/'

    source = rss.find('./{%s}channel/{%s}title' % (ns1,ns1)).text

    for item in rss.findall('./{%s}item' % ns1):
        attr = { 'source': source}
        for e in item:
            if e.tag == '{%s}title' % ns1:
                attr['title'] = e.text
            elif e.tag == '{%s}description' % ns1:
                attr['desc'] = e.text
            elif e.tag == '{%s}origLink' % ns2:
                attr['link'] = e.text
            elif e.tag == '{%s}date' % ns3:
                m     = re.match(r"^\s*(\d\d\d\d)-(\d\d)-(\d\d)T",e.text)
                year  = int(m.group(1))
                month = int(m.group(2))
                day   = int(m.group(3))
                attr['date']  = datetime.date(year,month,day)
        addPost(attr)

def addPost (a):
    if len(Post.objects.filter(link=a['link'])) == 0:
        Post(source=a['source'], title=a['title'], desc=a['desc'], link=a['link'], date=a['date'], rating=getRating(a['title'])).save()

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
