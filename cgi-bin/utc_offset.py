#!/opt/rh/python27/root/usr/bin/python
#!/usr/bin/python
from __future__ import print_function
import time
import sys
import cgi
import os
import urllib
import timezone_db
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
  localip = "192.168.7.42"
if 'macaddress' in fields:
  macaddress = fields['macaddress']
else:
  macaddress = 'NA'
if 'dev_type' in fields:
  dev_type = fields['dev_type']
else:
  raise Exception("Unrecognized request.")
  dev_type = 'Not given'

print ("Content-type: text/json\n\n") ### start responce immediatly to prevent timeout errors?
print('{')

tz = timezone_db.select(ip, localip, macaddress, dev_type)
# print ("tz:", tz)
version = sys.version_info
major, minor, micro = version[:3]
py_version = "%d.%d.%d" %(major, minor, micro)
tz["python version"] = py_version
tz["utc"] = int(time.time())
def format_utc_offset(x):
    '''add "+" back into utc_offset'''
    if type(x) == type(0):
        out = '%+05d' % x
    else:
        out = x
    return out

keys = tz.keys()
for i, k in enumerate(keys):
    v = tz[k]
    if k == 'utc_offset':
        v = format_utc_offset(v)
    print ('    "%s": "%s"' % (k, v), end='')
    if i < len(keys) - 1:
        print(',')
    else:
        print()
 # print ('    localip: "%s"' % fields['localip'])
print('}')

