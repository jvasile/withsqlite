from __future__ import print_function, unicode_literals
import unittest
import tempfile
from withsqlite import sqlite_db


class WithSQLiteTest(unittest.TestCase):
    def setUp(self):
        self.db = sqlite_db('test')
        self.db.begin()

    def tearDown(self):
        self.db.clear()
        self.db.save()

    def test_empty(self):
        self.assertEqual(self.db.items(), [])

    def test_add_one_string(self):
        self.db['a'] = 'test'
        items = self.db.items()
        self.assertEqual(len(items), 1)
        k, v = items[0]
        self.assertEqual(k, 'a')
        self.assertEqual(v, 'test')

    def test_add_two_strings(self):
        self.db['a'] = 'test_a'
        self.db['b'] = 'test_b'
        items = self.db.items()
        self.assertEqual(len(items), 2)
        k, v = items[0]
        self.assertEqual(k, 'a')
        self.assertEqual(v, 'test_a')
        k, v = items[1]
        self.assertEqual(k, 'b')
        self.assertEqual(v, 'test_b')

    def test_add_a_list(self):
        self.db['list'] = [1, 2, 3, 4, 5]
        items = self.db.items()
        self.assertEqual(len(items), 1)
        k, v = items[0]
        self.assertEqual(k, 'list')
        self.assertEqual(v, [1, 2, 3, 4, 5])

    def test_del_value(self):
        self.db['a'] = 'value_a'
        self.db['some'] = 'to be deleted'
        self.assertEqual(len(self.db.items()), 2)
        del self.db['some']
        self.assertEqual(len(self.db.items()), 1)
        self.assertIsNone(self.db.get('some'))
        try:
            self.db['some']
            self.assertEqual(1, 0, "__getitem__")
        except KeyError:
            pass

    def test_keys(self):
        values = ['a', 'b', 'c']
        for val in values:
            self.db[val] = val.upper()
        self.assertEqual(set(self.db.keys()), set(values))

    def test_values(self):
        values = ['A', 'B', 'C']
        for val in values:
            self.db[val.lower()] = val
        self.assertEqual(set(self.db.values()), set(values))

    def test_get(self):
        self.assertEqual(self.db.get('some', 5), 5)

    def test_repr(self):
        adict = {'a': 'A'}
        self.db['a'] = 'A'
        self.assertEqual(repr(adict), repr(self.db))

    def test_contains(self):
        self.db['key'] = 'value'
        self.assertTrue('key' in self.db)
        self.assertFalse('value' in self.db)

    def test_update(self):
        self.db['key'] = 'value'
        self.assertEqual(self.db['key'], 'value')
        self.db['key'] = 'foobar'
        self.assertEqual(self.db['key'], 'foobar')

    def test_dir(self):
        workdir = tempfile.mkdtemp()
        with sqlite_db("test", dir=workdir) as db:
            db['testing'] = 'dir'
        with sqlite_db("test", dir=workdir) as db:
            self.assertEqual(db['testing'], 'dir')

    def test_transaction(self):
        a = sqlite_db("test")
        with a.transaction():
            a['key'] = 'value'
            self.assertEqual(len(a.items()), 1)
            self.assertEqual(len(self.db.items()), 0)
        items = self.db.items()
        self.assertEqual(len(items), 1)
        k, v = items[0]
        self.assertEqual('key', k)
        self.assertEqual('value', v)

    def test_with(self):
        with sqlite_db("test") as db:
            db['a'] = 'test_a'
            db['b'] = 'test_b'
            items = db.items()
            self.assertEqual(len(items), 2)
            k, v = items[0]
            self.assertEqual(k, 'a')
            self.assertEqual(v, 'test_a')
            k, v = items[1]
            self.assertEqual(k, 'b')
            self.assertEqual(v, 'test_b')
