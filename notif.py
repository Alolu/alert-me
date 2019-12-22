# -*- coding: utf-8 -*-
import bs4 as bs
import requests as r
import re
import os
from tinydb import TinyDB, Query
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()
db = TinyDB('db.json')
dateMatch = [
    u'janvier',
    u'février',
    u'mars',
    u'avril',
    u'mai',
    u'juin',
    u'juillet',
    u'aout',
    u'septembre',
    u'octobre',
    u'novembre',
    u'décembre'
]

interestMatch = [
    "nuggets",
    "offre",
    "profiter"
]

def today(s):
    return not any(re.compile(re.escape(date)).search(s) for date in dateMatch)
def interest(s):
    return any(re.compile(r'(?i)' + words).search(s) for words in interestMatch)

def getPosts(src):
    soup = bs.BeautifulSoup(src.content.decode('utf-8','ignore'),'html.parser')
    allposts = soup.find("div", class_="_1xnd")
    posts = allposts.find_all("span", class_="timestampContent",text=today)
    for post in posts:
        lepost = post.find_parent("div", class_="_4-u2 _4-u8")
        link = post.parent.parent["href"]
        if lepost.find(text=interest) and not db.search(Query().link == link):
            #sendPromo("http://facebook.com" + link)
            db.insert({'link': link})

def sendPromo(link):
    r.post(os.environ.get("HOOK"),json={
        "text": link,
        "unfurl_links": True
    })

@sched.scheduled_job('interval',seconds=5)
def timed_job():
    print(os.environ.get("HOOK"))
    #getPosts(r.get('https://www.facebook.com/pg/mcdodainville/posts/?ref=page_internal'))
    sendPromo("test")
sched.start()
 