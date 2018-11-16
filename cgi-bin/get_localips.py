#!/usr/bin/python
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
 
except:
  ip = "1.2.3.4"

def get_localips():
  sql = '''
  SELECT localip, dev_type 
  FROM Device  
  WHERE ip="%s" AND localip != "NA" AND last_update > %s 
  ORDER BY localip''' % (ip, int(time.time() - 8 * 86400))
  cur = db.execute(sql)
  return [{"localip":l.decode('utf-8'), 'dev_type':t.decode('utf-8')} for l,t in cur.fetchall()]

print ("Content-type: text/json\n\n")

localips = get_localips()
n = len(localips)
print('{"localips": [')
for i in range(n):
    s = '{"localip": "%s", "dev_type": "%s"}' % (localips[i]["localip"], localips[i]["dev_type"])
    if i == n - 1:
        pass
    else:
        s = s + ','
    print(s)
print("]}")

