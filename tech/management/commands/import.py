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
        feeds = [ [ 'http://feeds.feedburner.com/readwriteweb',                  ''                            ],
                  [ 'http://feeds.feedburner.com/TechCrunch/',                   ''                            ],
                  [ 'http://feeds.feedburner.com/oreilly/radar/atom',            'http://www.w3.org/2005/Atom' ],
                  [ 'http://feeds.arstechnica.com/arstechnica/index?format=xml', ''                            ],
                  [ 'http://rss.slashdot.org/Slashdot/slashdot',                 'http://purl.org/rss/1.0/'    ],
                ]

        postAttrs = []
        for feed in feeds:
            postAttrs += feedburner(feed)

        for a in postAttrs:
            post = Post(source=a['source'], title=a['title'], desc=a['desc'], link=a['link'], date=a['date'], rating=getRating(a['title']))
            if len(Post.objects.filter(link=a['link'])) == 0:
                post.save()
            else:
                self.stdout.write("The following post already exists: " + str(post) + "\n")

'''
        for poll_id in args:
            try:
                poll = Poll.objects.get(pk=int(poll_id))
            except Poll.DoesNotExist:
                raise CommandError('Poll "%s" does not exist' % poll_id)
'''

def feedburner (feed):
    html = urllib2.urlopen(feed[0]).read()
    rss = xml.etree.ElementTree.XML(html)
    #xml.etree.ElementTree.dump(rss)

    if len(feed[1]) == 0:
        ns = ''
    else:
        ns = '{%s}' % feed[1]

    source = rss.find('./%schannel/%stitle' % (ns,ns))
    if source != None:
        source = source.text
    else:
        source = rss.find('./%stitle' % ns).text

    source = re.match(r"[a-zA-Z0-9_\s']+",source).group(0).strip()

    postAttrs = []
    for item in rss.findall('./channel/%sitem' % ns) + rss.findall('./%sitem' % ns) + rss.findall('./%sentry' % ns):
        attr = { 'source': source }
        for e in item:
            if e.tag == '%stitle' % ns:
                attr['title'] = e.text
            elif e.tag == '%sdescription' % ns:
                attr['desc'] = e.text
            elif e.tag == '%scontent' % ns:
                attr['desc'] = e.text
            elif e.tag == '{http://rssnamespace.org/feedburner/ext/1.0}origLink':
                attr['link'] = e.text
            elif e.tag == 'pubDate':
                m     = re.search(r'(\d+)\s+(\w+)\s+(\d+)',e.text)
                day   = int(m.group(1))
                month = months[m.group(2).strip().lower()]
                year  = int(m.group(3))
                attr['date']  = datetime.date(year,month,day)
            elif e.tag == '{http://purl.org/dc/elements/1.1/}date' or e.tag == '%spublished' % ns:
                m     = re.match(r"\s*(\d\d\d\d)-(\d\d)-(\d\d)T",e.text)
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
