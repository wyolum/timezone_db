import urllib.request

url = 'https://www.wyolum.com/utc_offset/utc_offset.py?refresh=5531&localip=192.168.1.183&macaddress=80:7D:3A:81:1B:10'
url = 'https://www.wyolum.com/utc_offset/hello.py'
response = urllib.request.urlopen(url)
data = response.read()      # a `bytes` object
text = data.decode('utf-8') # a `str`; this step can't be used if data is binary

print (text)
