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
 

except:
  ip = "1.2.3.4"
  localip = "192.168.1.123"
  macaddress = 'made:up:mac:address'
  fields = {'localip':localip, 'macaddress':macaddress} 

localip = "192.168.1.123"
tz = timezone_db.select(ip, localip, macaddress, 'CLOCKIOT')
tz = 'TIMEZONE'
body = '''Hello World, how are things at %s

tz: %s
''' % (ip, tz)

print ("Content-type: text/html\n\n")
print("<HEAD>HELLO</HEAD><BODY>%s</BODY>" % body)
