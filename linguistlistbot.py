from bs4 import BeautifulSoup
import requests
import re
import pickle
import datetime
from mastodon import Mastodon
import time

current_year = datetime.datetime.now().year

current_month = datetime.datetime.now().month - 1

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 
              'August', 'September', 'October', 'November', 'December']

pg = "http://listserv.linguistlist.org/pipermail/linguist/%d-%s/date.html" % (current_year, months[current_month])

r = requests.get(pg)

t = BeautifulSoup(r.text, "html.parser")

def linkCombiner(page):
    final = pg[:-9]+page['href']
    return final

def findData(t, link):
    
    page = t.findAll(text=True)

    title = t.select("title")[0].get_text()

    title = re.sub("\d\d.\d{3}, ", "", title)
    
    txt = ""

    for x in page:
        txt = txt + x

    idx = re.search("===\n", txt).span()[0]

    txt = txt[idx:]

    idx = re.search("Date: ", txt).span()[1]

    lines = txt[idx:].split("\n")

    message = title + "\n"
    
    for x in lines:
        if x.startswith("Location:"):
            message = message + x + "\n"
        elif x.startswith("Date: "):
            message = message + x + "\n"
        elif x.startswith("Subject: "):
            message = message + x + "\n"
        elif x.startswith("Meeting URL: "):
            message = message + x + "\n"

    message = message + link + "\n"

    return message

li = [x.find("a") for x in t.findAll("li")]

litxt = [x.text for x in li]

with open("last.pickle", "rb") as last:
    last = pickle.load(last)    

new_posts = []

if litxt[-3] != last:
    try:
        idx = litxt.index(last)
        for x in li[idx+1:-2]:
#            print(x)
            new_posts.append(x)

    except ValueError:
        idx = 0
        for x in li[idx:-2]:
#            print(x)
            new_posts.append(x)


new_messages = []

for x in new_posts:
    
    if ", Calls:" in x.text:
        new = requests.get(pg[:-9]+x['href'])
        new = BeautifulSoup(new.text, "lxml")

        new_messages.append(findData(new, linkCombiner(x)))
        print("added")
        
    elif ", Confs:" in x.text:
        new = requests.get(pg[:-9]+x['href'])
        new = BeautifulSoup(new.text, "lxml")
        new_messages.append(findData(new, linkCombiner(x)))
        print("added")
        
with open("last.pickle", "wb") as last2:
    pickle.dump(li[-3].text, last2)

api = Mastodon(
    
    access_token = "",
    api_base_url = ""
    
)

for x in new_messages:
    time.sleep(200)
    api.toot(x)
