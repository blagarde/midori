#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sqlite3
import codecs
from midori_parseutils import parser, meanings, kun, on

PLACEHOLDER= '?' # For SQLite. See DBAPI paramstyle.
JLPT_DEFAULT = 2
ITEM_TYPE = 'compound'
LIMIT = 10


decode = lambda x: codecs.decode(x, 'utf8')


class Dictionary():
    name = 'midori' # Backend identifier

    def __init__(self, db_name):
        conn = sqlite3.connect(db_name)
        self.curs = conn.cursor()
        self.db = db_name

    def lookup(self, value):
        value = '%' + value + '%'
        compounds = self.compound_lookup(value)
        kanjis = self.kanji_lookup(value)
        return compounds, kanjis

    def compound_lookup(self, value):
        query = "SELECT id, meaning, word1, word2 FROM entry WHERE word1 LIKE ? OR word2 LIKE ? OR meaning LIKE ? LIMIT ?"
        results = self.curs.execute(query, (value, value, value, LIMIT))
        return [Compound(row) for row in results.fetchall()]

    def kanji_lookup(self, value, by='literal', limit=LIMIT, recurse=False):
        query = "SELECT literal, meaning, reading_on, reading_kun FROM kanji WHERE literal LIKE ? OR meaning LIKE ? LIMIT ?"
        results = self.curs.execute(query, (value, value, LIMIT))
        return [Kanji(row) for row in results.fetchall()]

    def new(self, old, params, n = 1):
        item_type = params.get('item_type', ITEM_TYPE)
        level_type = params.get('jlpt_level', 'jlpt_level')
        level = params.get('level', JLPT_DEFAULT)
        assert level_type in ['jlpt_level', 'grade']
        placeholders= ', '.join(PLACEHOLDER for unused in old)

        query = "SELECT id, meaning, word1, word2 FROM entry \
                WHERE jlpt_level >= ? AND id NOT IN (%s) ORDER BY RANDOM() LIMIT %i" % (placeholders, n)

        if item_type == 'kanji':
            query = "SELECT literal, meaning, reading_on, reading_kun FROM kanji \
            WHERE grade <= ? AND literal NOT IN (%s) ORDER BY RANDOM() LIMIT %i" % (placeholders, n)

            if level_type == 'jlpt_level':
                query = "SELECT literal, meaning, reading_on, reading_kun FROM kanji \
                WHERE jlpt_level >= ? AND literal NOT IN (%s) ORDER BY RANDOM() LIMIT %i" % (placeholders, n)


        Entry = {"kanji":Kanji, "compound":Compound}[item_type]
        results = self.curs.execute(query, tuple([level] + old)).fetchall()
        entries = [Entry(*result) for result in results]
        if len(entries) == 1:
            return entries[0]
        return entries

class Compound():
    def __init__(self, row):
        uid, meaning_str, kanji_str, kana_str = row

        self.raw_meaning = meaning_str
        self.raw_kanji = kanji_str
        self.raw_kana = kana_str

        self.meanings = parser.parseString(meaning_str) if meaning_str != '' else []
        self.kanji = parser.parseString(kanji_str) if kanji_str != '' else []
        self.kana = parser.parseString(kana_str) if kana_str != '' else []

        def to_str(title, parsed):
            mystr = title + ':\n'
            for i, item in enumerate(parsed):
                mystr += str(i) + ': ' +   ','.join(item.words)
                if item.pos != '':
                    mystr += ' [' + ','.join(item.pos) + ']'
                if item.tags != '':
                    mystr += ' (' + ' | '.join(item.tags) + ')'
                if item.comment != '':
                    mystr += ' [' + ','.join(item.comment) + ']'
                mystr += '\n'
            return mystr

        self.meaning_str = to_str('Meanings', self.meanings)
        self.kanji_str = to_str('Writings', self.kanji)
        self.kana_str = to_str('Readings', self.kana)

        self.valid_answers = {
            "meaning2kanji" : [k for kl in self.kanji for k in kl.words],
            "kanji2kana" : [k for kl in self.kana for k in kl.words]
        }

        self.cue = {
            "meaning2kanji" : self.meaning_str + '\n' + self.kana_str,
            "kanji2kana" : self.kanji_str
        }

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        meanings_str = self.meaning_str
        kanji_str = self.kanji_str
        kana_str = self.kana_str
        display =   str(self.uid) + '\n' + \
                    meanings_str + '\n' + \
                    kanji_str + '\n' + \
                    kana_str + '\n'

        return display.encode("utf8")

    def __repr__(self):
        return self.kanji_str.encode("utf8")

class Kanji():
    def __init__(self, row):
        uid, meaning_str, on_str, kun_str = row
        self.uid = uid

        self.raw_meaning = meaning_str
        self.raw_on = on_str
        self.raw_kun = kun_str

        self.meanings = [] if meaning_str == '' else meanings.parseString(meaning_str)
        self.on = [] if on_str == '' else on.parseString(on_str)
        self.kun = [] if kun_str == '' else kun.parseString(kun_str)
        self.meaning_str = 'Meanings: ' + ','.join(self.meanings)
        self.on_str = u'音: ' + ','.join(self.on) 
        self.kun_str = u'訓: ' + ','.join(['.'.join(i) for i in self.kun])

        self.valid_answers = {
            "kanji2meaning" : list(self.meanings),
            "meaning2kanji" : list(self.uid)
        }

        self.cue = {
            "kanji2meaning" : self.uid,
            "meaning2kanji" : self.meaning_str + '\n' + self.on_str + '\n' + self.kun_str
        }


    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        display =   self.uid + '\n' + \
                    self.meaning_str + '\n' + \
                    self.on_str + '\n' + \
                    self.kun_str + '\n'
        return display.encode("utf8")

    def __repr__(self):
        return self.uid.encode("utf8")
