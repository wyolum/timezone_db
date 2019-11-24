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
  f = cgi.FieldStorage()
  fields = {}
  for k in f:
    fields[k] = f[k].value
  if 'macaddress' in fields:
    macaddress = fields['macaddress']
  else:
    macaddress = 'NA'
  if 'globalip' in fields:
    globalip = fields['globalip']
  else:
    globalip = 'NA'

except:
  ip = "1.2.3.4"
  localip = "192.168.1.123"
  localip = "192.168.7.XXX"
  macaddress = 'made:up:mac:address'
  fields = {'localip':localip, 'macaddress':macaddress} 
  globalip = ip
  

url = "https://ipapi.co/%s/json" % globalip

body = urllib.urlopen(url).read()
print("Content-type: text/html\n\n")
print(body)
