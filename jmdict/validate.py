from lxml import etree
import urllib2
from StringIO import StringIO
import gzip

JMDICT_GZ = 'http://ftp.monash.edu.au/pub/nihongo/JMdict.gz'
DTD = 'jmdict.dtd'


print "Downloading JMDict..."
response = urllib2.urlopen(JMDICT_GZ)
content = StringIO(response.read())
f = gzip.GzipFile(fileobj=content)
print "Validating JMDict XML..."
jmdict = etree.XML(f.read())
dtd = etree.DTD(open(DTD))
print "Pass" if dtd.validate(jmdict) else "Fail"
