from __future__ import print_function

import sqlite3

class Table:
    def __init__(self, name, db, *columns):
        self.name = name
        self.columns = columns
        self.db = db
    def create(self, print_only=False):
        cols = ['%s' % col for col in self.columns]
        sql = 'CREATE TABLE IF NOT EXISTS %s (%s);' % (self.name, ','.join(cols))
        if print_only:
            print(sql)
        else:
            self.db.execute(sql)
    def drop(self):
        sql = 'DROP TABLE %s' % self.name
        response = input('Warning, dropping table %s\nY to confirm: ' % self.name)
        if response[0] == 'Y':
            self.db.execute(sql)
            print ('%s Dropped' % self.name)
        else:
            print ('Drop not executed')
    def create_index(self, colnames, unique=False):
        idx_name = ''.join(colnames) + 'idx'
        cols = ','.join(colnames)
        unique = ['', 'UNIQUE'][unique]
        sql = 'CREATE %s INDEX %s ON %s(%s)' % (unique, idx_name, self.name, cols)

        self.db.execute(sql)
    def insert(self, values):
        place_holders = ','.join('?' * len(values[0]))
        cols = ','.join([col.name for col in self.columns])
        sql = 'INSERT INTO %s(%s) VALUES (%s);' % (self.name, cols, place_holders)
        rowcount = 0
        for row in values:
            ### add quote to string fields
            try:
                rowcount += self.db.executemany(sql, [row]).rowcount
            except sqlite3.IntegrityError:
                raise
                sql = 'select ip, macaddress from IP_Timezone'
                cur = self.db.execute(sql)
                for row in cur.fetchall():
                    print (row)
                pass
            self.db.commit()
        return rowcount

    def select(self, where=None):
        sql = 'SELECT * FROM %s' % self.name
        if where is not None:
            sql += ' WHERE ' + where
        cur = self.db.execute(sql)
        out = []
        colnames = [col.name for col in self.columns]
        for row in cur.fetchall():
            l = dict(zip(colnames, row))
            out.append(l)
        # print(sql, out)
        return out

    def join(self, other, col, where=None):
        sql = 'SELECT * FROM %s LEFT JOIN %s ON %s.%s' % (self.name, other.name, self.name, col)
        if where:
            sql += ' WHERE ' + where
        cur = self.db.execute(sql)
        colnames = [l[0] for l in cur.description]
        out = []
        for row in cur.fetchall():
            l = dict(zip(colnames, row))
            out.append(l)
        return out
        
class Column:
    def __init__(self, name, type, **kw):
        self.name = name
        self.type = type
        self.kw = kw
    def __str__(self):
        kw = ''
        for k in self.kw:
            if self.kw[k]:
                if type(self.kw[k]) == type(""):
                    kw = kw + ' ' + '%s %s' % (k.upper(), self.kw[k])
                else:
                    kw = kw + ' ' + '%s' % (k.upper())
        return '%s %s %s' % (self.name, self.type.name, kw)
    
class DBType:
    def __init__(self, name):
        self.name = name
class Integer(DBType):
    def __init__(self):
        DBType.__init__(self, 'INTEGER')
class Float(DBType):
    def __init__(self):
        DBType.__init__(self, 'FLOAT')
class String(DBType):
    def __init__(self):
        DBType.__init__(self, 'STRING')
class Boolean(DBType):
    def __init__(self):
        DBType.__init__(self, 'BOOLEAN')
class Text(DBType):
    def __init__(self):
        DBType.__init__(self, 'TEXT')
class TimeStamp(DBType):
    def __init__(self):
        DBType.__init__(self, 'TIMESTAMP')
