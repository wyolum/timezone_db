#!/usr/bin/python
from __future__ import print_function
import sqlite3
import urllib
import os
import database
from database import Column, String, Float, Integer
import json
import time
from datetime import datetime, timedelta
import cgi

try:
    ip = cgi.escape(os.environ["REMOTE_ADDR"])
    f = cgi.FieldStorage()
    fields = {}
    for k in f:
        fields[k] = f[k].value
    if 'localip' not in fields:
        fields['localip'] = 'NA'
    if 'macaddress' not in fields:
        fields['macaddress'] = 'NA'
except:
    ip = "1.2.3.4"
    ip = "108.56.138.39"
    localip = "192.168.1.1"
    macaddress = 'junk:mac:address'
    dev_type = "ClockIOT"
    fields = {'localip':localip, 'macaddress':macaddress, 'dev_type':dev_type}

DB_FN = 'timezone.db'
db = sqlite3.connect(DB_FN)

Timezones = database.Table('IP_Timezone', db,
                           Column('last_update', Integer()),
                           Column('count', Integer()),
                           Column('ip',String()),
                           Column('city', String()),
                           Column('region', String()),
                           Column('country_name', String()),
                           Column('timezone', String()),
                           Column('utc_offset', String()),
                           Column('latitude',Float()),
                           Column('longitude',Float()),
                           Column('localip',String()),
                           Column('macaddress',String()),
                           Column('dev_type',String())
                           )

def create_db():
    Timezones.create()
    idx_cols = ['ip', 'macaddress']
    Timezones.create_index(idx_cols, unique=True)


cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = 'IP_Timezone';")
create_flag = len(cursor.fetchall()) == 1

if not create_flag:
    create_db()

def lookup(ip, localip, macaddress, dev_type):
    url = "https://ipapi.co/%s/json" % ip
    s = urllib.urlopen(url).read()
    out = json.loads(s)
    out['last_update'] = int(time.time())
    out['macaddress'] = macaddress
    keep = [col.name for col in Timezones.columns]
    toss = []
    for name in out:
        if name not in keep:
            toss.append(name)
    for t in toss:
        del out[t]
    return out
    
def select(ip, localip, macaddress, dev_type):
    # print("select(%s,%s)" % (ip, macaddress))
    out = Timezones.select(where='ip="%s" AND macaddress="%s"' % (ip, macaddress))
    if not out:
        out = lookup(ip, localip, macaddress, dev_type)
        insert(ip, localip, macaddress, dev_type, out)
    else:
        out = out[0]
        update(ip, localip, macaddress, dev_type, out)
    return out

def insert(ip, localip, macaddress, dev_type, json_data):
    if "utc_offset" in json_data:
        j = json_data
        j['count'] = 1
        j['localip'] = localip
        j['macaddress'] = macaddress
        j['dev_type'] = dev_type
        values = []
        for col in Timezones.columns:
            values.append('%s' % j[col.name])
        try:
            Timezones.insert([values])
            # print()
            db.commit()
        except sqlite3.IntegrityError:
            raise
    else:
        ### data not available, let arduino handle this problem
        pass
    
def update(ip, localip, macaddress, dev_type, json_data):
    '''Update count and TZ if necessary'''
    # print("update()")
    j = json_data
    
    today = datetime.now()
    wkday = today.weekday()
    sunday = today - timedelta(days=wkday + 1, hours=today.hour, minutes=today.minute, seconds=today.second) + timedelta(hours=3)
    newest = int(time.mktime(sunday.timetuple()))

    if j['last_update'] < newest: ## refresh timezone offset and access count
        new_tz = lookup(ip, localip, macaddress, dev_type)
        j['last_update'] = new_tz['last_update']
        j['utc_offset'] = new_tz['utc_offset']
        j['localip'] = localip
        ### update calleres count... update all records with same ip.
        sql = '''\
UPDATE IP_Timezone 
SET 
    count=count+1,last_update="%s",localip="%s", utc_offset="%s" 
WHERE 
    ip="%s" AND macaddress="%s"''' % (j['last_update'], j['localip'], j['utc_offset'], j['ip'], j['macaddress'])
        db.execute(sql)
    else: ## still fresh, only update count
        sql = 'UPDATE IP_Timezone SET count=count+1 WHERE ip="%s"' % j['ip']
        db.execute(sql)
    # print(sql)
    db.commit()
    j['count'] = j['count'] + 1
