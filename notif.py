# -*- coding: utf-8 -*-
import bs4 as bs
import requests as r
import re
import os
from tinydb import TinyDB, Query
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()
db = TinyDB('db.json')
hook = os.environ.get("HOOK")

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
    u'décembre',
    u'January',
    u'February',
    u'March',
    u'April',
    u'May',
    u'June',
    u'July',
    u'August',
    u'September',
    u'November',
    u'December'
]
interestMatch = [
    "nuggets",
    "offre",
    "profiter"
]

#Filter functions
def today(s):
    return not any(re.compile(re.escape(date)).search(s) for date in dateMatch)
def interest(s):
    return any(re.compile(r'(?i)' + words).search(s) for words in interestMatch)

#Get posts from page and search for post containing our filters
def getPosts(src):
    soup = bs.BeautifulSoup(src.content.decode('utf-8','ignore'),'html.parser')
    allposts = soup.find("div", class_="_1xnd")
    posts = allposts.find_all("span", class_="timestampContent",text=today)
    for post in posts:
        lepost = post.find_parent("div", class_="_4-u2 _4-u8")
        link = post.parent.parent["href"]
        if lepost.find(text=interest) and not db.search(Query().link == link):
            print("Relevant post found : http://facebook.com" + link)
            sendPromo("http://facebook.com" + link)
            print("Storing in database...")
            db.insert({'link': link})
    if not posts:
        print("No relevant post found...")
#Webhook handler
def sendPromo(link):
    print("Sending to webhook...")
    r.post(hook,json={
        "text": link,
        "unfurl_links": True
    })

#Scheduled tasks to be ran every 30 minutes
@sched.scheduled_job('interval', minutes=30)
def timed_job():
    print("-> Fetching data from facebook")
    getPosts(r.get('https://www.facebook.com/pg/mcdodainville/posts/?ref=page_internal'))
    print("<- Job done")

print("-->Scheduler started")
sched.start()
 