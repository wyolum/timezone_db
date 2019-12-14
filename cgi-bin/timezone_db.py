from __future__ import print_function
import sqlite3
import sys
if sys.version_info[0] > 2:
    from urllib.request import urlopen
else:
    from urllib import urlopen
import os
import database
from database import Column, String, Float, Integer
import json
import time
from datetime import datetime, timedelta
import cgi
import ssl

ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

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

Timezone = database.Table('Timezone', db,
                          Column('first_update', Integer()),
                          Column('last_update', Integer()),
                          Column('tz_count', Integer()),
                          Column('timezone', String()),
                          Column('utc_offset', String()),
)

Device = database.Table('Device', db,
                        Column('timezone_rowid', Integer()),
                        Column('first_update', Integer()),
                        Column('last_update', Integer()),
                        Column('count', Integer()),
                        Column('ip',String()),
                        Column('latitude',Float()),
                        Column('longitude',Float()),
                        Column('city', String()),
                        Column('region', String()),
                        Column('country_name', String()),
                        Column('localip',String()),
                        Column('macaddress',String()),
                        Column('dev_type',String())
)

class RPIIPAddr(database.Table):
    def __init__(self):
          self.name = 'RPI_IP_ADDR'
          database.Table.__init__(self, self.name,  db,
                                  Column('sqltime', database.TimeStamp(), default="CURRENT_TIMESTAMP"),
                                  Column('IP_Addr', database.String()))
    def latest(self):
        sql = '''\
SELECT IP_Addr FROM %s ORDER BY sqltime DESC LIMIT 1
''' % self.name
        cursor = self.db.execute(sql)
        return cursor.fetchone()[0]
RPI_IP_Addr = RPIIPAddr()

def create_db():
    tz_idx_cols = ['timezone']
    Timezone.create()
    Timezone.create_index(tz_idx_cols, unique=True)
    
    dev_idx_cols = ['ip', 'macaddress']
    Device.create()
    Device.create_index(dev_idx_cols, unique=True)

    RPI_IP_Addr.create()
    db.commit()

def lookup(ip, localip, macaddress, dev_type):
    url = "https://ipapi.co/%s/json" % ip
    s = urlopen(url, context=ctx).read().decode('utf-8')
    # rpi_ip = RPI_IP_Addr.latest()
    # url = "http://%s/cgi-bin/ipapi.py?globalip=%s" % (rpi_ip, ip)
    # print(url)
    s = urlopen(url).read().decode('utf-8')
    out = json.loads(s)
    out['source'] = url
    out['last_update'] = int(time.time())
    out['macaddress'] = macaddress
    keep = [col.name for col in Timezone.columns] + [col.name for col in Device.columns]
    keep.append("source")
    toss = []
    for name in out:
        if name not in keep:
            toss.append(name)
    for t in toss:
        del out[t]
    return out
    
def select(ip, localip, macaddress, dev_type):
    columns = ['Timezone.' + col.name for col in Timezone.columns] + ['Device.' + col.name for col in Device.columns]
    columns = ','.join(columns)
    sql = '''\
SELECT
    %s
FROM 
  Timezone
INNER JOIN 
  Device ON Device.timezone_rowid = Timezone.rowid
WHERE
  Device.ip="%s" AND Device.macaddress="%s"
''' % (columns, ip, macaddress)
    cur = db.execute(sql)
    rows = cur.fetchall()
    rowcount = len(rows)
    if rowcount < 1:
        out = lookup(ip, localip, macaddress, dev_type)
        insert(ip, localip, macaddress, dev_type, out)
    elif rowcount == 1:
        names = [l[0] for l in cur.description]
        out = rows[0]
        out = dict(zip(names, out))
        out['source'] = 'cache'
        update(ip, localip, macaddress, dev_type, out)
    else:
        raise ValueError("More than one (%d) record returned" % cur.rowcount)
    return out

def insert(ip, localip, macaddress, dev_type, json_data):
    now = int(time.time())
    if "utc_offset" in json_data:
        ### create record if this is a new timezone
        sql = '''\
        SELECT rowid FROM Timezone WHERE Timezone.timezone = "%s"
        ''' % json_data['timezone']
        cur = db.execute(sql)
        data = cur.fetchall()
        if len(data) < 1:
            ### insert new timezone
            sql = '''\
            INSERT INTO Timezone (first_update, last_update, tz_count, timezone, utc_offset)
            VALUES (%d, 0, "%s", "%s")
            ''' % (now, now, json_data['timezone'], json_data['utc_offset'])
            cur = db.execute(sql)
            rowid = cur.lastrowid
            db.commit()
        elif len(data) == 1:
            rowid = data[0][0]
            ### update existing timezone
            sql = '''\
            UPDATE Timezone SET last_update = %s, tz_count = tz_count + 1, utc_offset="%s" WHERE rowid=%d
            ''' % (now, json_data['utc_offset'], rowid)
            db.execute(sql)
        else:
            raise ValueError("More than one (%d) record returned" % cur.rowcount)
        ### now Timezone table is update... insert into Device table
        j = json_data
        j['timezone_rowid'] = rowid
        j['last_update'] = now
        j['count'] = 0;
        j['localip'] = localip
        j['dev_type'] = dev_type
        if j['latitude'] is None:
            j['latitude'] = 0
        if j['longitude'] is None:
            j['longitude'] = 0
        sql = '''\
INSERT INTO Device (timezone_rowid, first_update, last_update, count, ip, latitude, longitude, city, region, country_name, localip, macaddress, dev_type)
VALUES (
%(timezone_rowid)d, %(last_update)d, %(last_update)d, %(count)d, "%(ip)s", %(latitude)f, %(longitude)f,"%(city)s", "%(region)s", "%(country_name)s", 
"%(localip)s","%(macaddress)s","%(dev_type)s")
''' % j
        try:
            db.execute(sql)
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
    j['localip'] = localip
    
    today = datetime.now()
    wkday = today.weekday()
    sunday = today - timedelta(days=wkday + 1, hours=today.hour, minutes=today.minute, seconds=today.second) + timedelta(hours=3)
    newest = int(time.mktime(sunday.timetuple()))

    if j['last_update'] < newest: ## refresh timezone offset
        new_tz = lookup(ip, localip, macaddress, dev_type)
        j['last_update'] = new_tz['last_update']
        j['utc_offset'] = new_tz['utc_offset']
    sql = '''\
UPDATE Timezone 
SET tz_count=tz_count+1, last_update=%s, utc_offset="%s"
WHERE Timezone.rowid=%d''' % (j['last_update'], j['utc_offset'], j['timezone_rowid'])
    db.execute(sql)
    
    now = int(time.time())
    sql = '''\
UPDATE Device 
SET count=count+1, last_update=%d, localip="%s", dev_type="%s", latitude=%.4f, longitude=%.4f, city="%s", region="%s", country_name="%s"
WHERE ip="%s" AND macaddress="%s"
''' % (now, localip, dev_type, j['latitude'], j['longitude'], j['city'], j['region'], j['country_name'], j['ip'], j['macaddress'])
    db.execute(sql)
    # print(sql)
    db.commit()
    j['count'] = j['count'] + 1

def test():
    print (select("108.56.138.39", "192.168.1.183", "80:7D:3A:8", "ClockIOT"))
if __name__ == '__main__':
    test()
