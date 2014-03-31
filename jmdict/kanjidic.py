from utils import obj_xml


KANJIDIC2_GZ = 'http://www.csse.monash.edu.au/~jwb/kanjidic2/kanjidic2.xml.gz'
KANJIDIC_DTD = 'kanjidic2.dtd'  # http://www.csse.monash.edu.au/~jwb/kanjidic2/kanjidic2_dtdh.html

get_kanjidic = lambda : obj_xml(KANJIDIC2_GZ, KANJIDIC_DTD)

gettext = lambda x: x.text
join = lambda x: '{'.join(x)
def getval(x, key):
    try:
        return gettext(getattr(x, key))
    except AttributeError:
        return 'None'


def char_info(c):
    assert c.find('reading_meaning') is not None
    freq, jlpt, grade = [getval(c.misc, i) for i in ('freq', 'jlpt', 'grade')]
    if freq == 'None':
        freq = '3000'
    kids = c.reading_meaning.rmgroup.getchildren()
    meanings = join([gettext(i) for i in kids if i.tag == 'meaning' and 'm_lang' not in i.attrib])
    on = join([gettext(i) for i in kids if i.tag == 'reading' and i.attrib.get('r_type', None) == 'ja_on'])
    kun = join([gettext(i) for i in kids if i.tag == 'reading' and i.attrib.get('r_type', None) == 'ja_kun'])
    return freq, jlpt, grade, meanings, on, kun
