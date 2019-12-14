#!/usr/bin/python
#!/opt/rh/python27/root/usr/bin/python
from __future__ import print_function

import sys
import cgi
import os
import urllib
import sqlite3
import database
import hits_db
import cgitb
cgitb.enable()

try:
  ip = cgi.escape(os.environ["REMOTE_ADDR"]) 
except:
  ip = '108.56.138.39'
  
f = cgi.FieldStorage()

fields = {}
for k in f:
  fields[k] = f[k].value
if 'localip' in fields:
  localip = fields['localip']
else:
  localip = 'NA'
if 'macaddress' in fields:
  macaddress = fields['macaddress']
else:
  macaddress = 'NA'
if 'dev_type' in fields:
  dev_type = fields['dev_type']
else:
  dev_type = 'Not given'
# fields['timezone'] = 'America/New_York'
# fields['timezone'] = 'Asia/Istanbul'
# fields['timezone'] = 'Asia/Kolkata'
if 'timezone' in fields:
  import arrow
  timezone = fields['timezone']
  utc = arrow.utcnow()
  try:
    current_time = utc.to(timezone)
    offset = current_time.utcoffset()
    offset = offset.days * 86400 + offset.seconds
    hh = int(offset / 3600.)
    mm = int((offset % 3600) / 60) 
    offset_string = '%+d%02d' % (hh, mm)
    current_time = '%4d-%02d-%02d %02d:%02d:%02d' % (current_time.year,
                                                     current_time.month,
                                                     current_time.day,
                                                     current_time.hour,
                                                     current_time.minute,
                                                     current_time.second)
    tz = {'utc_offset':offset_string,
          'ip':ip,
          'localip':localip,
          'macaddress':macaddress,
          'dev_type':dev_type,
          'timezone':timezone,
          'current_time':current_time}
  except:
    tz = {'utc_offset': 'Not Found',
          'timezone':timezone}
else:
  tz = {}
# print ("tz:", tz)
version = sys.version_info
major, minor, micro = version[:3]
py_version = "%d.%d.%d" %(major, minor, micro)
tz["python version"] = py_version
  
hits_db.insert(ip, localip, os.environ.get('SCRIPT_NAME') + '?' + os.getenv("QUERY_STRING"))

print ("Content-type: text/json\n\n")
print('{')

keys = tz.keys()
for i, k in enumerate(keys):
    v = tz[k]
    print ('    "%s": "%s"' % (k, v), end='')
    if i < len(keys) - 1:
        print(',')
    else:
        print()
 # print ('    localip: "%s"' % fields['localip'])
print('}')
