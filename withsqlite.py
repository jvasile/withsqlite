#!/usr/bin/env python 

"""
withsqlite - uses an sqlite db as a back end for a dict-like object,
kind of like shelve but with json and sqlite3.

Copyright 2011 James Vasile
Released under the GNU General Public License, version 3 or later.
See https://www.gnu.org/licenses/gpl-3.0.html for terms.

Repo is at <http://github.com/jvasile/withsqlite>.  Patches welcome!

This file was developed as part of planeteria <http://github.com/jvasile/planeteria>

"""
import os, sys, sqlite3, time
import simplejson as json

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

BUGS:

vals are json serialized before being written, so if you can't
serialize it, you can't put it in the dict.

Unimplemented mapping API:
a.copy() 	a (shallow) copy of a 	
a.update([b]) 	updates a with key/value pairs from b, overwriting existing keys, returns None 
a.fromkeys(seq[, value]) 	Creates a new dictionary with keys from seq and values set to value 
a.setdefault(k[, x]) 	a[k] if k in a, else x (also setting it)
a.pop(k[, x]) 	a[k] if k in a, else x (and remove k)
a.popitem() 	remove and return an arbitrary (key, value) pair 
a.iteritems() 	return an iterator over (key, value) pairs
a.iterkeys() 	return an iterator over the mapping's keys
a.itervalues() 	return an iterator over the mapping's values
"""

   def __init__(self, fname):
      self.fname = fname + ".sqlite3"
   def __enter__(self):
      if not os.path.exists(self.fname):
         self.make_db()
      self.conn = sqlite3.connect(self.fname)
      self.crsr = self.conn.cursor()
      return self
   def __exit__(self, type, value, traceback):
      self.conn.commit()
      self.crsr.close()
   def make_db(self):
      conn = sqlite3.connect(self.fname)
      c = conn.cursor()
      c.execute('''create table store (key text unique, val text)''')
      conn.commit()
      c.close()
   def __delitem__(self, key):
      """del a[k] 	remove a[k] from a"""
      self.crsr.execute("delete from store where key=?", [key])
   def jsonize(self,val):
      "If it's just a string, serialize it ourselves"
      if isinstance(val, basestring):
         return '"%s"' % val
      return json.dumps(val, default=to_json, sort_keys=True, indent=3)
   def __setitem__(self, key, val):
      """a[k] = v 	set a[k] to v 	"""

      try:
         if val == self.__getitem__(key):
            return
         self.crsr.execute("update or fail store set val=? where key==?", [self.jsonize(val), key])
      except KeyError:
         self.crsr.execute("insert into store values (?, ?)", [key, self.jsonize(val)])
   def __getitem__(self, key):
      """a[k] 	the item of a with key k 	(1), (10)"""
      self.crsr.execute('select val from store where key=?', [key])
      try:
         f = self.crsr.fetchone()[0]
      except TypeError:
         raise KeyError, key
      return json.loads(f)
   def __contains__(self, key):
      """k in a 	True if a has a key k, else False
         k not in a 	Equivalent to not k in a"""
      self.crsr.execute("select COUNT(*) from store where key=?", [key])
      return self.crsr.fetchone()[0] != 0
   def has_key(self, key):
      return self.__contains__(key)
   def __len__(self):
      """len(a) 	the number of items in a"""
      self.crsr.execute("select COUNT(*) from store")
      return self.crsr.fetchone()[0]
   def keys(self):
      """a.keys() 	a copy of a's list of keys"""
      self.crsr.execute("select key from store")
      return [f[0] for f in self.crsr.fetchall()]
   def values(self):
      """a.values() 	a copy of a's list of values"""
      self.crsr.execute("select val from store")
      return [f[0] for f in self.crsr.fetchall()]
   def items(self):
      """a.items() 	a copy of a's list of (key, value) pairs"""
      self.crsr.execute("select * from store")
      return self.crsr.fetchall()
   def get(self, k, x=None):
      """a.get(k[, x]) 	a[k] if k in a, else x """
      try:
         return self.__getitem__(k)
      except KeyError:
         return x

   def clear(self):
      """a.clear() 	remove all items from a"""
      self.crsr.execute("delete from store")

if __name__=="__main__":
   ## This would really be better as proper tests
   with sqlite_db("test") as db:
      db.clear()
      db['a']="test"
      db['as']="test"
      db['b']=[1,2,3,4,5]
      db['c']=[1,2,3,4,5]
      db['d']="who?"
      del db['b']
      print len(db)
      print db.keys()
      print db.values()
      print db.items()
      print db.get('b',5)
      print db.get('b')
      print db.get('c',5)
      print 'as' in db
      print 'asdf' not in db
      print db.has_key('as')
