import argparse
import csv
import getpass
import os
import owncloud
import re
import sys
import io
from lxml import etree

def validate_year_folder(oc, year_path):
  '''
     A year folder should be in the form (18|19|20)/d{2}
  '''

  errors = []

  pieces = year_path.split()
  if year_path[-1:] == '/':
    pieces.pop()

  if not re.match('^.*[/]\d{4}$', year_path):
    errors.append(year_path + ' is not a valid year.')

  for entry in oc.list(year_path):
    if entry.file_type == 'dir':
      if not re.match('^.*[/]\d{4}[/]$', entry.path):
        errors.append(year_path + ' contains folders that are not mmdd.')
    else:
      if not re.match('^.*\.csv$', entry.path):
        errors.append(year_path + ' contains files that are not .csv.')

  return errors

def validate_date_folder(oc, date_path):
  '''
     A date folder should be mmdd. 
     output: list of validation errors. 
  '''

  errors = []

  pieces = date_path.split('/')
  pieces.pop()
  month_date = pieces.pop()

  if int(month_date[:2]) < 1:
    errors.append(date_path + ' is not a valid date.')

  if int(month_date[:2]) > 12:
    errors.append(date_path + ' is not a valid date.')

  if int(month_date[2:4]) < 1:
    errors.append(date_path + ' is not a valid date.')

  if int(month_date[2:4]) > 31:
    errors.append(date_path + ' is not a valid date.')

  return errors

def get_identifier(path):
  pieces = entry.path.split('/')
  if entry.path[-1:] == '/':
    pieces.pop()
  entry_filename = pieces.pop()
  
  identifier = []

  while True:
    piece = pieces.pop()
    if piece == 'mvol':
      identifier = [piece] + pieces[0:1]

  return '-'.join(identifier)
   
def validate_folder(oc, date_path, folder_type, extension):
  errors = []

  folder_exists = False
  for entry in oc.list(date_path):
    if '/' + folder_type + '/' in entry.path and entry.file_type == 'dir':
      folder_exists = True

  if folder_exists:
    for entry in oc.list(date_path + '/' + folder_type):
      if not entry.file_type == 'file':
        errors.append(date_path + '/' + folder_type + '/ contains things that are not files.')

      identifier_match = get_identifier(entry.path).replace('-', '\-')
   
      if not re.match(identifier_match + '\d{4}\.' + extension + '$', entry.path):
        errors.append(date_math + '/' + folder_type + ' contains incorrectly named files.')
  else:
    errors.append(date_path + ' does not include an ALTO directory.')

  return errors

def validate_alto_folder(oc, date_path):
  return validate_folder(oc, date_path, 'ALTO', 'xml')

def validate_jpeg_folder(date_path):
  return validate_folders(oc, date_path, 'JPEG', 'jpg')

def validate_tiff_folder(date_path):
  return validate_folders(oc, date_path, 'TIFF', 'tif')

def validate_dc_xml(oc, identifier, f):
  """Make sure that a given dc.xml file is well-formed and valid, and that the
     date element is arranged as yyyy-mm-dd. 

     Arguments:
     oc -- an owncloud object, or None, for testing.
     f  -- a file object containing a dc.xml file. 
  """

  dtdf = io.StringIO("""<!ELEMENT metadata (title,date,description,identifier)>
                        <!ELEMENT title (#PCDATA)>
                        <!ELEMENT date (#PCDATA)>
                        <!ELEMENT description (#PCDATA)>
                        <!ELEMENT identifier (#PCDATA)>""")
  dtd = etree.DTD(dtdf)
  dtdf.close()

  errors = []

  try:
    metadata = etree.fromstring(f.read())
    if not dtd.validate(metadata):
      errors.append(identifier + ' is not valid.')
    else:
      datepull = etree.ElementTree(metadata).findtext("date")
      pattern = re.compile("^\d{4}-\d{2}-\d{2}")
      attemptmatch = pattern.fullmatch(datepull)
      if attemptmatch:
        sections = [int(s) for s in re.findall(r'\b\d+\b', datepull)]
        if (sections[0] < 1700) | (sections[0] > 2100):
          errors.append(identifier + ' has an incorrect year field.')
        if (sections[1] < 1) | (sections[1] > 12):
          errors.append(identifier + ' has an incorrect month field.')
        if (sections[2] < 1) | (sections[2] > 31):
          errors.append(identifier + ' has an incorrect day field.')
      else:
        errors.append(identifier + ' has a date with a wrong format')
  except etree.XMLSyntaxError as e:
    errors.append(identifier + ' is not well-formed.')

  return errors

def validate_mets_xml(oc, identifier, f):
  """Make sure that a given mets file is well-formed and valid.

     Arguments:
     oc -- an owncloud object, or None, for testing.
     f  -- a file object containing a mets.xml file. 
  """
  errors = []
  
  schemfd = open("mets.xsd.xml", 'r', encoding = 'utf8') #alternatively StringIO
  schemdoc = etree.parse(schemfd)
  schemfd.close()
  xmlschema = etree.XMLSchema(schemdoc)

  fdoc = etree.fromstring(f.read())
  if not xmlschema.validate(fdoc):
    errors.append(identifier + ' is not well-formed.')

  return errors

def validate_pdf(oc, identifier, f):
  """Make sure that a given PDF is valid.

     Arguments:
     oc -- an owncloud object, or None, for testing.
     f  -- a file object containing a PDF.
  """

  raise NotImplementedError

def validate_struct_txt(oc, identifier, f):
  """Make sure that a given struct.txt is valid. It should be tab-delimited
     data, with a header row. Each record should contains a field for object,
     page and milestone.

     Arguments:
     oc -- an owncloud object, or None, for testing.
     f  -- a file object containing a struct.txt file.
  """
 
  raise NotImplementedError

def get_identifier_from_path(path):
  pieces = path.split('/')

  if path[-1:] == '/':
    pieces.pop()
    
  while pieces[0] != 'mvol':
    pieces.pop(0)
  return '-'.join(pieces)

if __name__ == '__main__':
  """ Produce an input file for a year's worth of mvol data.
      This checks to be sure that files are available via specific URLs, and it produces an input file for the OCR building script. 
  """

  parser = argparse.ArgumentParser()
  parser.add_argument("username", help="WebDAV username.")
  parser.add_argument("directory", help="e.g. IIIF_Files/mvol/0004/1931")
  args = parser.parse_args()

  try:
    oc = owncloud.Client(os.environ['WEBDAV_CLIENT'])
  except KeyError:
    sys.stderr.write("WEBDAV_CLIENT environmental variable not set.\n")
    sys.exit()

  password = getpass.getpass('WebDAV password: ')
  oc.login(args.username, password)

  errors = []

  errors = errors + validate_year_folder(oc, args.directory)

  for date_folder in oc.list(args.directory):
    if date_folder.file_type == 'dir':
      errors = errors + validate_date_folder(oc, date_folder.path)

  for e in errors:
    print(e)
  
