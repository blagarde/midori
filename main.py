#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
from kivy.app import App
from kivy.uix.label import Label
from midori import Dictionary


LIMIT = 100

class MultiLineLabel(Label):
    pass


def get_label_text(parsed):
    make_clickable = lambda w: "[ref=" + w + ']' + w + "[/ref]"
    mystr = ''
    for i, item in enumerate(parsed):
        words = map(make_clickable, list(item.words))
        mystr += str(i) + ': ' +   ', '.join(words)
        if item.pos != '':
            mystr += ' [' + ','.join(item.pos) + ']'
        if item.tags != '':
            mystr += ' (' + ' | '.join(item.tags) + ')'
        if item.comment != '':
            mystr += ' [' + ','.join(item.comment) + ']'
        mystr += '\n'
    return mystr


def render_kanji(k):
    make_clickable = lambda w: "[ref=" + w + ']' + w + "[/ref]"
    large = lambda w: "[size=50]" + w + "[/size]"
    mystr = large(make_clickable(k.uid)) + '\n'
    words = map(make_clickable, list(k.meanings.words))
    mystr += ', '.join(words)
    on, kun = map(make_clickable, k.on), map(make_clickable, ['.'.join(i) for i in k.kun])
    mystr += u'\n音: ' + ', '.join(on)
    mystr += u'\n訓: ' + ', '.join(kun)
    return mystr


def render_compound(c):
    lst = [c.kanji, c.kana, c.meanings]
    return '\n'.join(map(get_label_text, lst))


class MainApp(App):
    def build(self):
        self.dct = Dictionary('midori.db')
        self.txt = self.root.ids['text']
        self.redraw('', [], [])

    def tap_entry(self, txt):
        compounds, kanjis = self.dct.lookup(txt)
        self.redraw(txt, kanjis, compounds)

    def search(self, btn_instance):
        txt = self.txt.text
        compounds, kanjis = self.dct.lookup(txt)
        self.redraw(txt, kanjis, compounds)

    def redraw(self, text, kanjis, compounds):
        self.txt.text = text
        grid = self.root.ids['grid']
        grid.clear_widgets()
        rendered_kanji = map(render_kanji, kanjis)
        rendered_compounds = map(render_compound, compounds)
        for txt in rendered_kanji[:LIMIT] + rendered_compounds[:LIMIT]:
            box = MultiLineLabel(text=txt, markup=True)
            grid.add_widget(box)

    def quit(self, inst):
        sys.exit(0)


if __name__ == "__main__":
    a = MainApp()
    a.run()