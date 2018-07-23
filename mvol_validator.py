import argparse
import csv
import getpass
import os
import owncloud
import re
import sys

def validate_year_folder(oc, year_path):
  '''
     A year folder should be in the form (18|19|20)/d{2}
  '''

  errors = []

  pieces = year_path.split()
  if year_path[-1:] == '/':
    pieces.pop()

  if not re.match('^.*[/]\d{4}[/]$', year_path):
    errors.append(year_path + ' is not a valid year.')

  for entry in oc.list(year_path):
    if not entry.file_type == 'dir':
      errors.append(year_path + ' contains entries that are not folders.')

    if not re.match('^.*[/]\d{4}[/]$', entry.path):
      errors.append(year_path + ' contains entries that are not mmdd.')

  return errors

def validate_date_folder(oc, date_path):
  '''
     A date folder should be mmdd. 
     output: list of validation errors. 
  '''

  errors = []

  pieces = entry.path.split('/')
  pieces.pop()
  month_date = pieces.pop()

  if int(month_date[:2]) < 1:
    errors.append(entry.path + ' is not a valid date.')

  if int(month_date[:2]) > 12:
    errors.append(entry.path + ' is not a valid date.')

  if int(month_date[2:4]) < 1:
    errors.append(entry.path + ' is not a valid date.')

  if int(month_date[2:4]) > 31:
    errors.append(entry.path + ' is not a valid date.')

  return errors

def validate_alto_folder(date_path):
  pass
  # ALTO exists and is a directory.
  # for each thing in ALTO:
  # it is a file.
  # it is in the form identifier_\d{4}.xml
  # it contains some content. 

def validate_jpeg_folder(date_path):
  pass
  # JPEG exists and is a directory.
  # for each thing in JEPG:
  # it is a file.
  # it is in the form identifier_\d{4}.jpg.
  # it is a jpeg.

def validate_tiff_folder(date_path):
  pass
  # TIFF exists and is a directory.
  # for each thing in TIFF:
  # it is a file.
  # it is in the form identifier_\d{4}.tif.
  # it is a tiff.

def validate_dc_xml(date_path):
  pass
  # get the identifier from this path.
  # a file exists that matches date_path/path.dc.xml.
  # it is an xml file. 
  # make sure it validates according to the dtd.
  # make sure the identifier is correct.
  # if we are in mvol-0004 make sure the date is correct.

def validate_mets_xml(date_path):
  pass
  # get the identifier from this path.
  # a file exists that matches date_path/path.mets.xml.
  # it is an xml file. 
  # make sure it validates.

def validate_pdf(date_path):
  pass
  # get the identifier from this path.
  # a file exists that matches date_path/path.pdf
  # it is a PDF.

def validate_struct_txt(date_path):
  pass
  # get the identifier from this path.
  # a file exists that matches date_path/identifier.struct.txt
  # every line contains three fields. 
  # the first row is for headers: it contains object, page, milestone. 

def validate_struct_txt(date_path):
  pass
  # get the identifier from this path.
  # a file exists that matches date_path/identifier.txt
  # it contains something. 

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

  errors = errors + validate_year_folder(args.directory)

  date_folders = []
  for date_folder in oc.list(args.directory):
    pieces = date_folder.path.split('/')
    if date_folder[-1:] == '/':
      pieces.pop()
    date_folders.append(pieces.pop())
  errors = errors + validate_date_folders(date_folders)
  

