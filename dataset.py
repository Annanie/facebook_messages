from bs4 import BeautifulSoup, NavigableString
from tqdm import tqdm
import pandas as pd
import requests
import sys

me = "100000503840103@facebook.com"
token = "EAACEdEose0cBAJUuIS5dzyNTBbZAONKFr9NzXqEDHRXWy7TGYnE5KIpHwvAVDadEgEHSZBpOE0wdopg05necxPiXjuZB7UybDniKUjiM1ZAVrPkM1ZA7C6XTLxZC9CePByA4h5jWNYulZBfXU2cooaJNvu85zVgbVYRG4kRZCG2WFZAvisCjf6ftZBkirs94x8K6kZD"

database = []
users = {}
errors = []

months =    {"January": "01",
            "February": "02",
            "March": "03",
            "April": "04",
            "May": "05",
            "June": "06",
            "July": "07",
            "August": "08",
            "September": "09",
            "October": "10",
            "November": "11",
            "December": "12"}

periods = { "am": 0,
            "pm": 12}

def get_person(uid):
    r = requests.get("https://graph.facebook.com/"+str(uid)+"?access_token="+str(token)).json()
    return [r['id'],r['first_name'],r['last_name'],r['name']]

def get_time(s):
    raw = s.split(", ")
    month, day = raw[1].split(" ")
    year, x, time, y = raw[2].split(" ")
    hour, minutes = time.split(":")
    p = minutes[2:]
    mi = int(minutes[:2])
    if mi < 10:
        mi = "0%d" %mi

    return "%s-%s-%s %d:%s:00" %(year,months[month],day,int(hour)+periods[p],str(mi))

def who(thread, users):
    people = [element for element in thread if isinstance(element, NavigableString)][0].split(", ")
    people.remove(me)
    person = people[0].split("@")[0]
    if person not in users:
        users[person] = get_person(person)[3]
    return users[person]

soup = BeautifulSoup(open('messages.htm'),"lxml")
threads = soup.find_all('div',{"class":"thread"})

for thread in tqdm(threads):
    try:
        person = who(thread, users)
    except:
        person = "Error"
        errors.append(thread)
    divs = thread.find_all('div',{"class":"message"})
    messages = thread.find_all('p')
    for (div, message) in zip(divs, messages):
        sent = False
        info = div.find_all('span')
        sender, time = info[0].text, info[1].text
        if ("@facebook" in sender and sender != me) or sender == person:
            sent = True
        lista = [person, sent, get_time(time), message.text, len(message.text)]
        database.append(lista)

df = pd.DataFrame(database,columns=["person","sent","time","text","len"])
df.to_pickle("database.pkl")


err = open('errors.txt','w')
err.write(str(errors))
err.close()
