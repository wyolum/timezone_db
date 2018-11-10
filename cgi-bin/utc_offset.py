#!/usr/bin/python
from __future__ import print_function
import cgi
import os
import urllib
import timezone_db
import cgitb
cgitb.enable()

try:
  ip = cgi.escape(os.environ["REMOTE_ADDR"]) 
except:
  ip = '1.2.3.4'
  
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

tz = timezone_db.select(ip, localip, macaddress, dev_type)
print ("tz:", tz)
def format_utc_offset(x):
    '''add "+" back into utc_offset'''
    if type(x) == type(0):
        out = '%+05d' % x
    else:
        out = x
    return out

print ("Content-type: text/json\n\n")
print('{')
for k in tz:
    v = tz[k]
    if k == 'utc_offset':
        v = format_utc_offset(v)
    print ('    "%s": "%s",' % (k, v))
 # print ('    localip: "%s"' % fields['localip'])
print('}')
