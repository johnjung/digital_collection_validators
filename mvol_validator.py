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

  errors = errors + validate_year_folder(oc, args.directory)

  for date_folder in oc.list(args.directory):
    if date_folder.file_type == 'dir':
      errors = errors + validate_date_folder(oc, date_folder.path)

  for e in errors:
    print(e)
  
