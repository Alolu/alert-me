# -*- coding: utf-8 -*-
import re
import os
import bs4 as bs
import requests as r
from tinydb import TinyDB, Query
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()
DB = TinyDB('db.json')
HOOK = os.environ.get("HOOK")

DATE_MATCH = [
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
INTEREST_MATCH = [
    "nuggets",
    "offre",
    "profiter"
]

def today(s):
    """Filtre BS4 permettant de recuperer tout les posts du jour uniquement"""
    return not any(re.compile(re.escape(date)).search(s) for date in DATE_MATCH)
def interest(s):
    """Filtre BS4 permettant de trouver les posts en rapports avec les mots recherchés"""
    return any(re.compile(r'(?i)' + words).search(s) for words in INTEREST_MATCH)

def get_posts(src):
    """Récupère les posts de facebook, prend en param une reponse get a facebook"""
    soup = bs.BeautifulSoup(src.content.decode('utf-8', 'ignore'),'html.parser')
    allposts = soup.find("div", class_="_1xnd")
    posts = allposts.find_all("span", class_="timestampContent",text=today)
    for post in posts:
        lepost = post.find_parent("div", class_="_4-u2 _4-u8")
        link = post.parent.parent["href"]
        if lepost.find(text=interest) and not DB.search(Query().link == link):
            print("Relevant post found : http://facebook.com" + link)
            send_promo("http://facebook.com" + link)
            print("Storing in database...")
            DB.insert({'link': link})
    if not posts:
        print("No relevant post found...")
#Webhook handler
def send_promo(link):
    """Envoie le lien du post a mon webhook Slack"""
    print("Sending to webhook...")
    r.post(HOOK,json={
        "text": link,
        "unfurl_links": True
    })

#Scheduled tasks to be ran every 30 minutes
@sched.scheduled_job('interval', minutes=30)
def timed_job():
    """Recupere les posts et les envois tout les 30mins"""
    print("-> Fetching data from facebook")
    get_posts(r.get('https://www.facebook.com/pg/mcdodainville/posts/?ref=page_internal'))
    print("<- Job done")

print("-->Scheduler started")
sched.start()
 