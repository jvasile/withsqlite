#!/usr/bin/env python

"""
withsqlite - uses an sqlite db as a back end for a dict-like object,
kind of like shelve but with json and sqlite3.

Copyright 2011-2013 James Vasile
Released under the GNU General Public License, version 3 or later.
See https://www.gnu.org/licenses/gpl-3.0.html for terms.

Repo is at <http://github.com/jvasile/withsqlite>.  Patches welcome!

This file was developed as part of planeteria
<http://github.com/jvasile/planeteria>

"""
import os
import sqlite3
import time
try:
    import simplejson as json
except ImportError:
    import json


def to_json(python_object):
    if isinstance(python_object, time.struct_time):
        return {'__class__': 'time.asctime',
                '__value__': time.asctime(python_object)}

    return {'__class__': 'basestring',
            '__value__': str(python_object)}


class sqlite_db():
    """
    Backends a dict on an sqlite db.  This class aims to present like a
    dict wherever it can.

    USE:
    import sqlite_db from withsqlite
    with sqlite_db("filename") as db:
       db['aaa'] = {'test':'ok'}
       print db.items()

    Specify a table to have one sqlite db hold multiple dicts:

    with sqlite_db("filename", table="fruit") as db:
       db['citrus'] = ['orange', 'grapefruit']
       print db.items()

    If you change the dict in any way, its state will differ from the
    state of the sqlite database.  Changes are committed to disk when you
    close the database connection, manually call commit, or (if you've set
    autocommit to True) after each assignment.

    KNOWN LIMITATION:

    vals are json serialized before being written, so if you can't
    serialize it, you can't put it in the dict.

    >>> with sqlite_db("test") as db:
    ...    db.clear()
    ...    db.items()
    ...
    []
    >>> with sqlite_db("test") as db:
    ...    db['a'] = "test"
    ...    db.items()
    ...
    [(u'a', u'test')]
    >>> with sqlite_db("test") as db:
    ...    db['as'] = "test"
    ...    db.items()
    ...
    [(u'a', u'test'), (u'as', u'test')]
    >>> with sqlite_db("test") as db:
    ...    db['b'] = [1,2,3,4,5]
    ...    del db['b']
    ...
    >>> with sqlite_db("test") as db:
    ...    db.items()
    ...    len(db)
    ...
    [(u'a', u'test'), (u'as', u'test')]
    2
    >>> with sqlite_db("test") as db:
    ...    db.keys()
    ...
    [u'a', u'as']
    >>> with sqlite_db("test") as db:
    ...    db.values()
    ...
    [u'test', u'test']
    >>> with sqlite_db("test") as db:
    ...    db.get('b', 5)
    ...
    5
    >>> with sqlite_db("test") as db:
    ...    db.get('b')
    ...
    >>> with sqlite_db("test") as db:
    ...    db.get('c',5)
    ...
    5
    >>> with sqlite_db("test") as db:
    ...    'as' in db
    ...
    True
    >>> with sqlite_db("test") as db:
    ...    'asdf' not in db
    ...
    True
    >>> with sqlite_db("test") as db:
    ...    db.has_key('as')
    ...
    True
    >>>
    """

    def __init__(self, fname, autocommit=False, table="store"):
        self.fname = '{}.sqlite3'.format(fname)
        self.autocommit = autocommit
        self.table = table
        self.conn = None
        self.crsr = None

    def __enter__(self):
        if not os.path.exists(self.fname):
            self.make_db()
        self._connect()
        return self

    def __exit__(self, type, value, traceback):
        self.commit()
        self.crsr.close()

    def _connect(self):
        if not self.conn:
            if self.autocommit:
                self.conn = sqlite3.connect(self.fname, isolation_level=None)
            else:
                self.conn = sqlite3.connect(self.fname)
        if not self.crsr:
            self.crsr = self.conn.cursor()

    def make_db(self):
        conn = sqlite3.connect(self.fname)
        crsr = conn.cursor()
        qry = "create table if not exists {} (key text unique, val text)"
        crsr.execute(qry.format(self.table))
        conn.commit()
        crsr.close()

    def commit(self):
        """This should rarely be necessary."""
        self.conn.commit()

    def __delitem__(self, key):
        """del a[k]   remove a[k] from a"""
        qry = "delete from {} where key=?"
        self.crsr.execute(qry.format(self.table), [key])

    def jsonize(self, val):
        "If it's just a string, serialize it ourselves"
        if isinstance(val, basestring):
            return '"{}"'.format(val)
        return json.dumps(val, default=to_json, sort_keys=True, indent=3)

    def __setitem__(self, key, val):
        """a[k] = v   set a[k] to v   """
        try:
            if val == self.__getitem__(key):
                return
            qry = "update or fail {} set val=? where key==?"
            self.crsr.execute(qry.format(self.table), [self.jsonize(val), key])
        except KeyError:
            qry = "insert into {} values (?, ?)"
            self.crsr.execute(qry.format(self.table), [key, self.jsonize(val)])

    def __getitem__(self, key):
        """a[k]   the item of a with key k    (1), (10)"""
        qry = 'select val from {} where key=?'
        self.crsr.execute(qry.format(self.table), [key])
        try:
            f = self.crsr.fetchone()[0]
        except TypeError:
            raise KeyError(key)
        return json.loads(f)

    def __contains__(self, key):
        """k in a     True if a has a key k, else False
        k not in a     Equivalent to not k in a"""
        qry = "select COUNT(*) from {} where key=?"
        self.crsr.execute(qry.format(self.table), [key])
        return self.crsr.fetchone()[0] != 0

    def has_key(self, key):
        return self.__contains__(key)

    def __len__(self):
        """len(a)     the number of items in a"""
        self.crsr.execute("select COUNT(*) from {}".format(self.table))
        return self.crsr.fetchone()[0]

    def keys(self):
        """a.keys()   a copy of a's list of keys"""
        self.crsr.execute("select key from {}".format(self.table))
        return [f[0] for f in self.crsr.fetchall()]

    def values(self):
        """a.values()     a copy of a's list of values"""
        self.crsr.execute("select val from {}".format(self.table))
        return [json.loads(f[0]) for f in self.crsr.fetchall()]

    def items(self):
        """a.items()  a copy of a's list of (key, value) pairs"""
        self.crsr.execute("select * from {}".format(self.table))
        return [(f[0], json.loads(f[1])) for f in self.crsr.fetchall()]

    def get(self, k, x=None):
        """a.get(k[, x])  a[k] if k in a, else x """
        try:
            return self.__getitem__(k)
        except KeyError:
            return x

    def clear(self):
        """a.clear()  remove all items from a"""
        self.crsr.execute("delete from {}".format(self.table))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
