import urllib2
import gzip
from StringIO import StringIO
from lxml import etree, objectify


isurl = lambda u: any([u.startswith(i + '://') for i in 'http https ftp'.split()])


def get_flike(xml_path):
    flike = StringIO(urllib2.urlopen(xml_path).read()) if isurl(xml_path) else open(xml_path)
    return gzip.GzipFile(fileobj=flike) if xml_path.endswith('.gz') else flike


def fetch_xml(xml_path, dtd=None):
    '''Download an XML and optionally validate it against a DTD.
    Both arguments can either local or web URLs, and optionnaly gzipped'''
    flike = get_flike(xml_path)
    if dtd is not None:
        print "Validating %s XML with %s DTD..." % (xml_path, dtd)
        xml = etree.XML(flike.read())
        dtd = etree.DTD(get_flike(dtd))
        dtd.validate(xml)
        flike.seek(0)
    return flike


def obj_xml(xml, dtd):
    fh = fetch_xml(xml, dtd=dtd)
    return objectify.fromstring(fh.read())
