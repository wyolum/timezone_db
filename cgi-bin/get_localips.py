#!/usr/bin/python
#!/opt/rh/python27/root/usr/bin/python
from __future__ import print_function
import cgi
import os
import urllib
import timezone_db
import sqlite3
import time
import cgitb
cgitb.enable()

DB_FN = 'timezone.db'
db = sqlite3.connect(DB_FN)

try:
  ip = cgi.escape(os.environ["REMOTE_ADDR"]) 
  f = cgi.FieldStorage()
  fields = {}
  for k in f:
    fields[k] = f[k].value
  if 'dev_type' in fields:
    dev_type = fields['dev_type']
  else:
    dev_type = 'ClockIOT' 
except:
  ip = "127.0.0.1"
  dev_type = "ClockIOT"
def get_localips():
  new_sql = '''
  SELECT localip, dev_type, last_update
  FROM Device  
  WHERE ip="%s" AND localip != "NA" AND last_update > %s AND dev_type like "%s" 
  ORDER BY localip''' % (ip, int(time.time() - 8 * 86400), dev_type)
  sql = '''
  SELECT localip, dev_type, last_update
  FROM Device  
  WHERE ip="%s" AND 
        localip != "NA" AND 
         -- last_update > %s AND 
        dev_type="ClockIOT" 
  ORDER BY last_update DESC''' % (ip, int(time.time() - 8 * 86400))
  works_sql = '''
  SELECT localip, dev_type, last_update
  FROM Device  
  WHERE ip="%s" AND localip != "NA"  
  ORDER BY localip''' % (ip, )
  cur = db.execute(sql)
  return [{"localip":l.decode('utf-8'), 'dev_type':t.decode('utf-8'), 'last_update':u} for l,t,u in cur.fetchall()]

print ("Content-type: text/json\n\n")

localips = get_localips()
n = len(localips)
print('{"localips": [')
for i in range(n):
    s = '{"localip": "%s", "dev_type": "%s", "last_update": "%d"}' % (localips[i]["localip"], localips[i]["dev_type"], localips[i]["last_update"])
    if i == n - 1:
        pass
    else:
        s = s + ','
    print(s)
print("]}")

