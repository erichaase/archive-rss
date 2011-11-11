from __future__ import division

from django.core.management.base import BaseCommand, CommandError
from tech.models import Post, LikeWordCount, DislikeWordCount

import urllib2
import xml.etree.ElementTree
import datetime
import re

months = {
    'jan': 1,
    'feb': 2,
    'mar': 3,
    'apr': 4,
    'may': 5,
    'jun': 6,
    'jul': 7,
    'aug': 8,
    'sep': 9,
    'oct': 10,
    'nov': 11,
    'dec': 12,
}

class Command(BaseCommand):
    help = 'Import posts from various RSS feeds'

    def handle (self, *args, **options):
        feeds = [ 'http://feeds.feedburner.com/readwriteweb',
                  'http://feeds.feedburner.com/TechCrunch/',
                  #'http://feeds.feedburner.com/oreilly/radar/atom',
                  'http://feeds.arstechnica.com/arstechnica/index?format=xml',
                  #'http://rss.slashdot.org/Slashdot/slashdot',
                ]

        postAttrs = slashdot()
        for feed in feeds:
            postAttrs += feedburner(feed)

        for a in postAttrs:
            post = Post(source=a['source'], title=a['title'], desc=a['desc'], link=a['link'], date=a['date'], rating=getRating(a['title']))
            if len(Post.objects.filter(link=a['link'])) == 0:
                post.save()
            else:
                self.stderr.write("The following post already exists: " + unicode(post) + "\n")

'''
        for poll_id in args:
            try:
                poll = Poll.objects.get(pk=int(poll_id))
            except Poll.DoesNotExist:
                raise CommandError('Poll "%s" does not exist' % poll_id)
'''

def feedburner (feed):
    html = urllib2.urlopen(feed).read()
    rss = xml.etree.ElementTree.XML(html)
    #xml.etree.ElementTree.dump(rss)

    source = rss.find('./channel/title').text

    print source
    postAttrs = []
    for item in rss.findall('./channel/item'):
        attr = { 'source': source}
        for e in item:
            if e.tag == 'title':
                attr['title'] = e.text
            elif e.tag == 'description':
                attr['desc'] = e.text
            elif e.tag == '{http://rssnamespace.org/feedburner/ext/1.0}origLink':
                attr['link'] = e.text
            elif e.tag == 'pubDate':
                m     = re.search(r'(\d+)\s+(\w+)\s+(\d+)',e.text)
                day   = int(m.group(1))
                month = months[m.group(2).strip().lower()]
                year  = int(m.group(3))
                attr['date']  = datetime.date(year,month,day)
        print attr['title']
        postAttrs.append(attr)
    print
    return postAttrs

def slashdot():
    html = urllib2.urlopen('http://rss.slashdot.org/Slashdot/slashdot').read()
    rss = xml.etree.ElementTree.XML(html)
    #xml.etree.ElementTree.dump(rss)

    ns1 = 'http://purl.org/rss/1.0/'
    ns2 = 'http://rssnamespace.org/feedburner/ext/1.0'
    ns3 = 'http://purl.org/dc/elements/1.1/'

    source = rss.find('./{%s}channel/{%s}title' % (ns1,ns1)).text

    postAttrs = []
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
        postAttrs.append(attr)
    return postAttrs

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
