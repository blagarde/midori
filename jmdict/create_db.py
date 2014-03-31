import sys

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData

from jmdict import get_jmdict, join
from kanjidic import get_kanjidic, char_info


if __name__ == "__main__":

    engine = create_engine('sqlite:///jmdict.db')

    metadata = MetaData()

    entry = Table('entry', metadata,
        Column('id', Integer, primary_key=True),
        Column('word1', String),
        Column('word2', String),
        Column('meaning', String),
    )

    kanji = Table('kanji', metadata,
        Column('literal', String, primary_key=True),
        Column('frequency', Integer),
        Column('jlpt', Integer),
        Column('grade', Integer),
        Column('reading_on', String),
        Column('reading_kun', String)
    )

    metadata.create_all(engine)

    jmdict, kanjidic = get_jmdict(), get_kanjidic()

    with engine.begin() as conn:
        for e in jmdict.find('entry'):
            seq_id = e.getchildren()[0]
            sys.stdout.write("\rMigrating entry %s..." % seq_id)
            sys.stdout.flush()
            w1, w2, mng =  join(e, 'k_ele'), join(e, 'r_ele'), join(e, 'sense')
            conn.execute(entry.insert(), id=str(seq_id), word1=w1, word2=w2, meaning=mng)
        print "Done."

        for i, k in enumerate(kanjidic.find('character')):
            if k.find('reading_meaning') is not None:
                literal = k.literal.text
                sys.stdout.write(u"\rMigrating kanji %s... %s" % (i, literal))
                sys.stdout.flush()
                freq, jlpt, grade, meanings, on, kun = char_info(k)
                conn.execute(kanji.insert(), literal=literal, reading_on=on, reading_kun=kun,
                    frequency=freq, jlpt=jlpt, grade=grade)
        print "Done."
