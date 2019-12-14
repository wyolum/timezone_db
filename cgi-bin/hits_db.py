import time
import sqlite3
from database import Integer, String, Column, Table

DB_FN = 'hits.db'
db = sqlite3.connect(DB_FN)

Hits = Table('hits', db,
                      Column('ip', String()),
                      Column('localip', String()),
                      Column('epoch', Integer()),
                      Column('request', String()),
                      )

Hits.create()

def insert(ip, localip, request):
    now = int(time.time())
    Hits.insert([[ip, localip, now, request]])
