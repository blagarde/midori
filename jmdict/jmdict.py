import os
from lxml import etree
from utils import fetch_xml, obj_xml


JMDICT_GZ = 'http://ftp.monash.edu.au/pub/nihongo/JMdict.gz'
# EDICT2_GZ = 'http://ftp.monash.edu.au/pub/nihongo/edict2.gz'


JMDICT_DTD = 'jmdict.dtd'
HERE = os.path.abspath(os.path.dirname(__file__))
jmdict_gz = os.path.join(HERE, 'JMdict.gz')
dtd = etree.DTD(fetch_xml(JMDICT_DTD))
entity_dct = {i.orig: i.name for i in dtd.entities()}


gettext = lambda x: x.text if len(x.items()) == 0 else None
getinfo = lambda x: entity_dct[x.text]
stitch = lambda x: '}'.join([f(c) for c in x.getchildren() if f(c) is not None])
ignore = lambda x: None
tag = lambda x: '[' + getinfo(x)
pos = lambda x: ']' + getinfo(x)
ant = lambda x: '\\' + gettext(x)
s_inf = lambda x: '`' + gettext(x)
def join(x, tag):
    return '{'.join([f(c) for c in x.getchildren() if c.tag == tag and f(c) is not None])

sortdict = {k: i for i, k in enumerate(entity_dct.values())}
sort_func = lambda x: sortdict.get(x, 0)

def sensefmt(sense):
    glosses = [f(k) for k in sense.getchildren() if k.tag == 'gloss' and f(k) is not None]
    rest = sorted([f(k) for k in sense.getchildren() if k.tag != 'gloss' and f(k) is not None], key=sort_func)
    return '}'.join(glosses + rest[::-1])

dispatch = {'k_ele': stitch, 'r_ele': stitch,
    're_restr': ant, 'ant': ant, 'pos': pos,
    's_inf': s_inf, 'sense': sensefmt,
    }

dispatch.update({field: gettext for field in ['keb', 'reb', 'gloss', 'xref']})
dispatch.update({field: tag for field in ['ke_inf', 're_inf', 'misc', 'dial']})
dispatch.update({field: ignore for field in ['re_nokanji', 'ke_pri', 're_pri', 'stagr', 'field', 'lsource', 'stagk']})
f = lambda x: dispatch[x.tag](x)

get_jmdict = lambda: obj_xml('JMdict', JMDICT_DTD)
