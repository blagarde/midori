from pyparsing import *

# define grammar
tagmark = Literal('[').suppress()
posmark = Literal(']').suppress()
commark = Literal('`').suppress()

jp_word = CharsNotIn('{}][`').setResultsName("words", listAllMatches = True)
tag = tagmark + jp_word.setResultsName("tags", listAllMatches = True)
pos = posmark + jp_word.setResultsName("pos", listAllMatches = True)
comment = commark + jp_word.setResultsName("comment", listAllMatches = True)


segment = jp_word | tag | pos | comment
segsep = Suppress(Word('}',exact=1))



# Compound
sep = Suppress(Word('{',exact=1))

meaning = Group(delimitedList(segment, segsep))
parser = delimitedList(meaning, sep)


# Kanji
stem = ending = CharsNotIn('{}][`.')
katakana = Word(srange(r"[\0x30A0-\0x30FF]"))
hiragana = Word(srange(r"[\0x3040-\0x309F]"))
brkmark = Literal('.').suppress()
kunword = Group(stem("stem") + Optional(brkmark + hiragana("ending")))

kun = delimitedList(kunword, sep)
on = delimitedList(katakana, sep)
meanings = delimitedList(jp_word, sep)

