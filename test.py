import io
import json
import unittest
import urllib.request
import os

from mvol_collection_year import IIIFCollectionYear
from mvol_collection_month import IIIFCollectionMonth
from mvol_manifest import IIIFManifest
from mvol_validator import validate_dc_xml, validate_mets_xml, validate_pdf, validate_struct_txt

from pathlib import Path

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

  def test_struct_bad(self):
    """catches illformed struct"""
    file = Path('testdocs/bad.struct.txt')
    f = open(file, 'r')
    self.assertTrue(validate_struct_txt(None, 'bad.struct.txt', f)[0] ==
      "bad.struct.txt has an error in line 4.")
    f.close()

  def test_struct_correct(self):
    """confirms struct is wellformed, without the extra empty line"""
    file = Path('testdocs/good.struct.txt')
    f = open(file, 'r')
    self.assertTrue(len(validate_struct_txt(None, 'good.struct.txt', f)) == 0)
    f.close()

  def test_struct_correct_extra_line(self):
    """confirms struct is wellformed, including ones with an extra empty line at end"""
    file = Path('testdocs/good_with_extra_line.struct.txt')
    f = open(file, 'r')
    self.assertTrue(len(validate_struct_txt(None, 'good_with_extra_line.struct.txt', f)) == 0)
    f.close()

  def test_pdf_notempty(self):
    """confirms pdf is nonempty, though not whether it's actually a pdf"""
    file = Path('testdocs/mini-sueto.pdf')
    f = open(file, 'r')
    self.assertTrue(len(validate_pdf(None, 'mini-sueto.pdf', f)) == 0)
    f.close()

  def test_pdf_empty(self):
    """catches if pdf is empty file"""
    file = Path('testdocs/empty.pdf')
    f = open(file, 'r')
    self.assertTrue(len(validate_pdf(None, 'empty.pdf', f)) > 0)
    f.close()

  def test_mets_xml_pass(self):
    """mets validator confirms wellformed xml following mets standards"""
    file = Path('testdocs/good.mets.xml')
    f = open(file, 'r')
    self.assertTrue(len(validate_mets_xml(None, 'good.mets.xml', f)) == 0)
    f.close()

  def test_mets_xml_wellformed_not_mets(self):
    """mets validator catches if wellformed, but not at mets standards"""
    file = Path('testdocs/mvol-0004-1942-0407.dc.xml')
    f = open(file, 'r')
    self.assertTrue(len(validate_mets_xml(None, 'mvol-0004-1942-0407.dc.xml', f)) > 0)
    f.close()

  def test_dc_xml_wellformedness(self):
    '''dc.xml validator catches well-formedness errors.'''
    xml_str = '<not_well></formed_xml>'
    f = io.StringIO(xml_str)
    self.assertTrue(len(validate_dc_xml(None, 'mvol-0004-1901-0101', f)) > 0)

  def test_dc_xml_outer_element(self):
    '''dc.xml validator makes sure outer element is <metadata>.'''
    xml_str = '<dublin_core><title>test</title><date>2000-01-01</date><description>test</description><identifier>mvol-0004-1900-0101</identifier></dublin_core>'
    f = io.StringIO(xml_str)
    self.assertTrue(len(validate_dc_xml(None, 'mvol-0004-1901-0101', f)) > 0)

  def test_dc_xml_date(self):
    '''dc.xml validator makes sure the text of the date element is yyyy-mm-dd.'''
    xml_str = '<metadata><title>test</title><date>2000-31-01</date><description>test</description><identifier>mvol-0004-1900-0101</identifier></metadata>'
    f = io.StringIO(xml_str)
    self.assertTrue(len(validate_dc_xml(None, 'mvol-0004-1901-0101', f)) > 0)

  def test_dc_xml(self):
    '''dc.xml validator accepts a correctly formed file.'''
    xml_str = '<metadata><title>test</title><date>2000-01-31</date><description>test</description><identifier>mvol-0004-1900-0101</identifier></metadata>'
    f = io.StringIO(xml_str)
    self.assertTrue(len(validate_dc_xml(None, 'mvol-0004-1901-0101', f)) == 0)

  def test_mets_xml_wellformedness(self):
    '''mets validator catches well-formedness errors.'''
    xml_str = '<not_well></formed_xml>'
    f = io.StringIO(xml_str)
    self.assertTrue(len(validate_mets_xml(None, 'mvol-0004-1901-0101', f)) > 0)

  def test_mets_xml_valid(self):
    '''mets validator catches validation errors.'''
    xml_str = '<mets:mets xmlns:mets="http://www.loc.gov/METS/"/>'
    f = io.StringIO(xml_str)
    self.assertTrue(len(validate_mets_xml(None, 'mvol-0004-1901-0101', f)) > 0)

  def test_mets_xml(self):
    '''mets validator produces no errors for a valid mets file.'''
    xml_str = '''<?xml version="1.0" encoding="UTF-8"?><mets:mets xmlns:mets="http://www.loc.gov/METS/" xmlns:lc="http://www.loc.gov/mets/profiles" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:rights="http://www.loc.gov/rights/" xmlns:mods="http://www.loc.gov/mods/v3" xmlns:bib="http://www.loc.gov/mets/profiles/modsBibCard" OBJID="loc.afc.afc9999005.1153" PROFILE="lc:modsBibCard">
      <mets:metsHdr LASTMODDATE="2016-08-09T12:12:51.320141-04:00"/>
      <mets:dmdSec ID="dmd1">
        <mets:mdWrap MDTYPE="MODS">
          <mets:xmlData>
    	<mods:mods ID="mods1" version="3.4">
    	  <mods:titleInfo>
    	    <mods:title>Alabama blues</mods:title>
    	  </mods:titleInfo>
    	  <mods:name type="personal">
    	    <mods:namePart>Lomax, Alan</mods:namePart>
    	    <mods:namePart type="date">1915-2002</mods:namePart>
    	    <mods:role>
    	      <mods:roleTerm type="text">Recordist</mods:roleTerm>
    	    </mods:role>
    	  </mods:name>
    	  <mods:name type="personal">
    	    <mods:namePart>Hurston, Zora Neale</mods:namePart>
    	    <mods:role>
    	      <mods:roleTerm type="text">Recordist</mods:roleTerm>
    	    </mods:role>
    	  </mods:name>
    	  <mods:name type="personal">
    	    <mods:namePart>Barnicle, Mary Elizabeth</mods:namePart>
    	    <mods:namePart type="date">1891-1978</mods:namePart>
    	    <mods:role>
    	      <mods:roleTerm type="text">Recordist</mods:roleTerm>
    	    </mods:role>
    	  </mods:name>
    	  <mods:name type="personal">
    	    <mods:namePart>Sapps, Booker T.</mods:namePart>
    	    <mods:role>
    	      <mods:roleTerm type="text">Performer</mods:roleTerm>
    	    </mods:role>
    	  </mods:name>
    	  <mods:name type="personal">
    	    <mods:namePart>Matthews, Roger</mods:namePart>
    	    <mods:role>
    	      <mods:roleTerm type="text">Performer</mods:roleTerm>
    	    </mods:role>
    	  </mods:name>
    	  <mods:name type="personal">
    	    <mods:namePart>Flowers, Willy</mods:namePart>
    	    <mods:role>
    	      <mods:roleTerm type="text">Performer</mods:roleTerm>
    	    </mods:role>
    	  </mods:name>
    	  <mods:typeOfResource>sound recording</mods:typeOfResource>
    	  <mods:language>
    	    <mods:languageTerm authority="iso639-2b" type="code">eng</mods:languageTerm>
    	  </mods:language>
    	  <mods:physicalDescription>
    	    <mods:form authority="gmd">sound recording</mods:form>
    	  </mods:physicalDescription>
    	  <mods:note type="statement of responsibility">Sung by Booker T. Sapps with harmonica, with harmonica by Roger Matthews, and guitar by Willy Flowers.</mods:note>
    	  <mods:note type="instrument">Harmonica (mouth organ)</mods:note>
    	  <mods:note type="instrument">Harmonica (mouth organ)</mods:note>
    	  <mods:note type="instrument">Guitar</mods:note>
    	  <mods:subject>
    	    <mods:hierarchicalGeographic>
    	      <mods:country>United States of America</mods:country>
    	      <mods:state>Florida</mods:state>
    	      <mods:city>Belle Glade</mods:city>
    	    </mods:hierarchicalGeographic>
    	  </mods:subject>
    	  <mods:relatedItem type="host">
    	    <mods:titleInfo>
    	      <mods:title>A. Lomax Z.N. Hurston and Barnicle Expedition</mods:title>
    	    </mods:titleInfo>
    	    <mods:identifier type="lccn">2008700301</mods:identifier>
    	  </mods:relatedItem>
    	  <mods:identifier type="AFC Number">AFC 1935/001</mods:identifier>
    	  <mods:relatedItem type="host">
    	    <mods:titleInfo>
    	      <mods:title> Traditional Music &amp; Spoken Word</mods:title>
    	    </mods:titleInfo>
    	    <mods:location>
    	      <mods:url>http://lcweb2.loc.gov/diglib/ihas/html/afccards/afccards-home.html</mods:url>
    	    </mods:location>
    	  </mods:relatedItem>
    	  <mods:identifier type="AFS Number">AFS 00368 A</mods:identifier>
    	  <mods:identifier type="AFS Number">AFS 00368 B</mods:identifier>
    	  <mods:identifier type="afsNum">368</mods:identifier>
    	  <mods:identifier type="afsNum">368</mods:identifier>
    	  <mods:location>
    	    <mods:physicalLocation>American Folklife Center, Library of Congress</mods:physicalLocation>
    	  </mods:location>
    	  <mods:location>
    	    <mods:physicalLocation authority="marcorg">DLC</mods:physicalLocation>
    	  </mods:location>
    	  <mods:recordInfo>
    	    <mods:recordContentSource>IHAS</mods:recordContentSource>
    	    <mods:recordChangeDate encoding="marc">160809</mods:recordChangeDate>
    	    <mods:recordIdentifier source="IHAS">loc.afc.afc9999005.1153</mods:recordIdentifier>
    	  </mods:recordInfo>
    	</mods:mods>
          </mets:xmlData>
        </mets:mdWrap>
      </mets:dmdSec>
      <mets:fileSec>
        <mets:fileGrp USE="MASTER">
          <mets:file MIMETYPE="image/tiff" GROUPID="G1" ID="f0178m">
    	<mets:FLocat LOCTYPE="URL" xlink:href="http://lcweb4.loc.gov/natlib/ihas/warehouse/afc9999005/AFS_300_A-734_B/0178.tif"/>
          </mets:file>
        </mets:fileGrp>
        <mets:fileGrp USE="SERVICE">
          <mets:file MIMETYPE="image/jpeg" GROUPID="G1" ID="f0178s">
    	<mets:FLocat LOCTYPE="URL" xlink:href="http://lcweb4.loc.gov/natlib/ihas/service/afc9999005/AFS_300_A-734_B/0178v.jpg"/>
          </mets:file>
          <mets:file MIMETYPE="image/tiff" GROUPID="G1" ID="f0178z">
    	<mets:FLocat LOCTYPE="URL" xlink:href="/media/loc.afc.afc9999005.1153/0178.tif"/>
          </mets:file>
        </mets:fileGrp>
      </mets:fileSec>
      <mets:structMap>
        <mets:div DMDID="dmd1" TYPE="bib:modsBibCard">
          <mets:div TYPE="bib:card">
    	<mets:div TYPE="lc:image">
    	  <mets:fptr FILEID="f0178m"/>
    	  <mets:fptr FILEID="f0178s"/>
    	  <mets:fptr FILEID="f0178z"/>
    	</mets:div>
          </mets:div>
        </mets:div>
      </mets:structMap>
    </mets:mets>'''
    f = io.StringIO(xml_str)
    self.assertTrue(len(validate_mets_xml(None, 'mvol-0004-1901-0101', f)) == 0)

  def test_pdf_is_not_zero_length(self):
    '''pdf validator makes sure PDF file contains some content.'''
    f = io.StringIO('')
    self.assertTrue(len(validate_pdf(None, 'mvol-0004-1901-0101', f)) > 0)

  def test_struct_txt_has_headers(self):
    '''struct.txt validator requires headers.'''
    f = io.StringIO('''00000001	1
00000002	2
00000003	3
00000004	4''')
    self.assertTrue(len(validate_struct_txt(None, 'mvol-0004-1901-0101', f)) > 0)

  def test_struct_txt_has_tabs(self):
    '''struct.txt validator requires headers.'''
    f = io.StringIO('''object,page,milestone
00000002,2,
00000003,3,
00000004,4,''')
    self.assertTrue(len(validate_struct_txt(None, 'mvol-0004-1901-0101', f)) > 0)

  def test_struct_txt_has_tabs(self):
    '''struct.txt validator requires headers.'''
    f = io.StringIO('''object	page	milestone
00000002	2
00000003	3
00000004	4''')
    self.assertTrue(len(validate_struct_txt(None, 'mvol-0004-1901-0101', f)) == 0)

if __name__ == '__main__':
  unittest.main()
