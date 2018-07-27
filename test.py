import io
import json
import unittest
import urllib.request
import os

from mvol_collection_year import IIIFCollectionYear
from mvol_collection_month import IIIFCollectionMonth
from mvol_manifest import IIIFManifest
from mvol_validator import validate_dc_xml
from mvol_validator import validate_mets_xml

def ordered(obj):
  if isinstance(obj, dict):
    return sorted((k, ordered(v)) for k, v in obj.items())
  if isinstance(obj, list):
    return sorted(ordered(x) for x in obj)
  else:
    return obj

class TestIIIFTools(unittest.TestCase):

  '''
  def test_iiif_collection_year(self): 
    url = 'http://iiif-collection.lib.uchicago.edu/mvol/0004/mvol-0004-1930.json'
    live_data = json.load(urllib.request.urlopen(url))
    test_data = IIIFCollectionYear(
      'Daily Maroon',
      'mvol-0004-1930',
      'A newspaper produced by students of the University of Chicago. Published 1900-1942 and continued by the Chicago Maroon.',
      'University of Chicago',
      '/Volumes/webdav/IIIF_Files/mvol/0004/1930'
    ).data()
    self.assertTrue(ordered(live_data) == ordered(test_data))

  def test_iiif_collection_month(self):
    url = 'http://iiif-collection.lib.uchicago.edu/mvol/0004/mvol-0004-1930-01.json'
    live_data = json.load(urllib.request.urlopen(url))
    test_data = IIIFCollectionMonth(
      'Daily Maroon',
      'mvol-0004-1930-01',
      'A newspaper produced by students of the University of Chicago. Published 1900-1942 and continued by the Chicago Maroon.',
      'University of Chicago',
      '/Volumes/webdav/IIIF_Files/mvol/0004/1930'
    ).data()
    self.assertTrue(ordered(live_data) == ordered(test_data))

  def test_iiif_manifest(self):
    url = 'http://iiif-manifest.lib.uchicago.edu/mvol/0004/1929/0103/mvol-0004-1929-0103.json'
    live_data = json.load(urllib.request.urlopen(url))
    test_data = IIIFManifest(
      'Daily Maroon',
      'mvol-0004-1929-0103',
      'A newspaper produced by students of the University of Chicago. Published 1900-1942 and continued by the Chicago Maroon.',
      'University of Chicago Library',
      '/Volumes/webdav/IIIF_Files/mvol/0004/1929'
    ).data()
    self.assertTrue(ordered(live_data) == ordered(test_data))
  '''

class TestMvolValidator(unittest.TestCase):

  def test_mets_xml_wellformedness_pass(self):
    fileDir = os.path.dirname(os.path.realpath('__file__'))
    file = os.path.join(fileDir, 'testdocs\good.xml')
    f = open(file, 'r')
    self.assertTrue(len(validate_mets_xml(None, 'good.xml', f)) == 0)

  def test_dc_xml_wellformedness(self):
    """dc.xml validator catches well-formedness errors."""
    xml_str = '<not_well></formed_xml>'
    f = io.StringIO(xml_str)
    self.assertTrue(len(validate_dc_xml(None, 'mvol-0004-1901-0101', f)) > 0)

  def test_dc_xml_outer_element(self):
    """dc.xml validator makes sure outer element is <metadata>."""
    xml_str = '<dublin_core><title>test</title><date>2000-01-01</date><description>test</description><identifier>mvol-0004-1900-0101</identifier></dublin_core>'
    f = io.StringIO(xml_str)
    self.assertTrue(len(validate_dc_xml(None, 'mvol-0004-1901-0101', f)) > 0)

  def test_dc_xml_date(self):
    """dc.xml validator makes sure the text of the date element is yyyy-mm-dd."""
    xml_str = '<metadata><title>test</title><date>2000-31-01</date><description>test</description><identifier>mvol-0004-1900-0101</identifier></metadata>'
    f = io.StringIO(xml_str)
    self.assertTrue(len(validate_dc_xml(None, 'mvol-0004-1901-0101', f)) > 0)

  def test_dc_xml(self):
    """dc.xml validator accepts a correctly formed file."""
    xml_str = '<metadata><title>test</title><date>2000-01-31</date><description>test</description><identifier>mvol-0004-1900-0101</identifier></metadata>'
    f = io.StringIO(xml_str)
    errors = validate_dc_xml(None, 'mvol-0004-1901-0101', f)
    print(errors)
    self.assertTrue(len(errors) == 0)
    
if __name__ == '__main__':
  unittest.main()
