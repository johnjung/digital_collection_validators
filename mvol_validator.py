import argparse
import csv
import getpass
import os
import owncloud
import re
import sys
import io
from lxml import etree

def get_ancestor_fileinfo(oc, f, n):
  """Get an ancestor owncloud.FileInfo object. 
     format (18|19|20)\d{2}

     Arguments:
     oc -- an owncloud object.
     f  -- an owncloud.FileInfo object.
     n  -- ancestor number. 1 = parent, 2 = grandparent, etc. 

     Returns:
     an owncloud.FileInfo object for a directory n levels up in the filesystem.
  """

  pieces = f.get_path().split('/')
  while n:
    pieces.pop()
    n = n - 1

  return oc.file_info('/'.join(pieces))

def get_identifier_from_fileinfo(oc, f):
  """Get an identifier string from a fileinfo object that represents a mmdd directory.

     Arguments:
     oc -- an owncloud object.
     f  -- an owncloud.FileInfo object.

     Returns:
     an identifier string, e.g. 'mvol-0004-1930-0103'.
  """
  return '%s-%s-%s-%s' % (
    get_ancestor_fileinfo(oc, f, 3).get_name(),
    get_ancestor_fileinfo(oc, f, 2).get_name(),
    get_ancestor_fileinfo(oc, f, 1).get_name(),
    f.get_name()
  )

def validate_mvol_directory(oc, identifier, f):
  """Make sure that the great-grandparent of this directory is a folder called
     'mvol'.

     Arguments:
     oc         -- an owncloud object.
     identifier -- for error messages.
     f          -- an owncloud.FileInfo object for an mvol mmdd directory.

     Returns:
     A list of error messages, or an empty list. 
  """

  if get_ancestor_fileinfo(oc, f, 3).get_name() == 'mvol':
    return []
  else:
    return [identifier + ' is contained in a great-grandparent folder that is not called "mvol".']

def validate_mvol_number_directory(oc, identifier, f):
  """Make sure that the grandparent of this directory is a four-digit mvol
     number, in the format /d{4}.

     Arguments:
     oc         -- an owncloud object.
     identifier -- for error messages.
     f          -- an owncloud.FileInfo object for an mvol mmdd directory.

     Returns:
     A list of error messages, or an empty list. 
  """

  if re.match('^\d{4}$', get_ancestor_fileinfo(oc, f, 2).get_name()):
    return []
  else:
    return [identifier + ' is contained in a grandparent folder that is not a valid mvol number.']

def validate_year_directory(oc, identifier, f):
  """Make sure that the parent of this directory is a year folder, in the
     format (18|19|20)\d{2}

     Arguments:
     oc         -- an owncloud object.
     identifier -- for error messages.
     f          -- an owncloud.FileInfo object for an mvol mmdd directory.

     Returns:
     A list of error messages, or an empty list. 
  """

  if re.match('^(18|19|20)\d{2}$', get_ancestor_fileinfo(oc, f, 1).get_name()):
    return []
  else:
    return [identifier + ' is contained in a parent folder that is not a valid year.']

def validate_date_directory(oc, identifier, f):
  """Make sure that this folder is in the format (0\d|1[012])[0123]\d.

     Arguments:
     oc         -- an owncloud object, or None, for testing.
     identifier -- for error messages.
     f          -- a file object that referrs to a mmdd directory.

     Returns:
     A list of error messages, or an empty list. 
  """

  if re.match('^(0\d|1[012])[0123]\d$', f.get_name()):
    return []
  else:
    return [identifier + ' is not a valid mmdd folder name.']

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

def validate_directory(oc, identifier, f, folder_name):
  """A helper function to validate ALTO, JPEG, and TIFF folders inside mmdd
     folders. 

     Arguments:
     oc          -- an owncloud object.
     identifier  -- for error messages.
     f           -- a file object that referrs to a mmdd directory (the parent
		    of the ALTO, JPEG, or TIFF directory being validated.)
     folder_name -- the name of the folder: ALTO|JPEG|TIFF

     Returns:
     A list of error messages, or an empty list. 
  """

  extensions = {
    'ALTO': 'xml',
    'JPEG': 'jpg',
    'TIFF': 'tif'
  }

  if not folder_name in extensions.keys():
    raise ValueError('unsupported folder_name.')

  errors = []

  filename_re = '^%s-%s-%s-%s_\d{4}\.%s$' % (
    get_ancestor_fileinfo(oc, f, 3).get_name(),
    get_ancestor_fileinfo(oc, f, 2).get_name(),
    get_ancestor_fileinfo(oc, f, 1).get_name(),
    f.get_name(),
    extensions[folder_name]
  )

  try:
    folder_f = oc.file_info(f.get_path() + '/' + folder_name)
    for entry in oc.list(folder_f.get_path()):
      if not entry.is_dir():
        if not re.match(filename_re, entry.get_name()):
          errors.append(identifier + '/' + folder_name + ' contains incorrectly named files.')
        if entry.get_size() == 0:
          errors.append(identifier + '/' + folder_name + ' contains a 0 byte file.')
  except owncloud.HTTPResponseError:
    errors.append(identifier + ' does not contain a ' + folder_name + ' folder.')

  return errors

def validate_alto_directory(oc, identifier, f):
  """Validate that an ALTO folder exists. Make sure it contains appropriate
     files.

     Arguments:
     oc          -- an owncloud object.
     identifier  -- for error messages.
     f           -- a file object that refers to a mmdd directory (the parent
                    of the directory being validated.)

     Returns:
     A list of error messages, or an empty list. 
  """
  return validate_directory(oc, identifier, f, 'ALTO')

def validate_jpeg_directory(oc, identifier, f):
  """Validate that an JPEG folder exists. Make sure it contains appropriate
     files.

     Arguments:
     oc          -- an owncloud object.
     identifier  -- for error messages.
     f           -- a file object that refers to a mmdd directory (the parent
                    of the directory being validated.)

     Returns:
     A list of error messages, or an empty list. 
  """
  return validate_directory(oc, identifier, f, 'JPEG')

def validate_tiff_directory(oc, identifier, f):
  """Validate that an TIFF folder exists. Make sure it contains appropriate
     files.

     Arguments:
     oc          -- an owncloud object.
     identifier  -- for error messages.
     f           -- a file object that refers to a mmdd directory (the parent
                    of the directory being validated.)

     Returns:
     A list of error messages, or an empty list. 
  """
  return validate_directory(oc, identifier, f, 'TIFF')

def _validate_dc_xml_file(oc, identifier, file_object):
  """Make sure that a given dc.xml file is well-formed and valid, and that the
     date element is arranged as yyyy-mm-dd. 

     Arguments:
     oc          -- an owncloud object, or None, for testing.
     identifier  -- for error messages.
     file_object -- a file object, the .dc.xml file.
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
    metadata = etree.fromstring(file_object.read())
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
    pass

  return errors

def validate_dc_xml(oc, identifier, file_info):
  """Make sure that a given dc.xml file is well-formed and valid, and that the
     date element is arranged as yyyy-mm-dd. 

     Arguments:
     oc         -- an owncloud object, or None, for testing.
     identifier -- for error messages.
     file_info  -- a fileinfo object, the mmdd directory containing the .dc.xml
                   file.
  """
  try:
    file_object = io.BytesIO(oc.get_file_contents('{}/{}.dc.xml'.format(
                    file_info.path, get_identifier_from_fileinfo(oc, f))))
    return _validate_dc_xml_file(oc, identifier, file_object)
  except owncloud.HTTPResponseError:
    return [identifier + '.dc.xml does not exist.']

def validate_mets_xml(oc, identifier, file_info):
  """Make sure that a given mets.xml file is well-formed and valid, and that the
     date element is arranged as yyyy-mm-dd. 

     Arguments:
     oc         -- an owncloud object, or None, for testing.
     identifier -- for error messages.
     file_info  -- a fileinfo object, the mmdd directory containing the .mets.xml
  """
  try:
    file_object = io.BytesIO(oc.get_file_contents('{}/{}.mets.xml'.format(
                    file_info.path, get_identifier_from_fileinfo(oc, f))))
    return _validate_mets_xml_file(oc, identifier, file_object)
  except owncloud.HTTPResponseError:
    return [identifier + '.mets.xml does not exist.']

def _validate_mets_xml_file(oc, identifier, f):
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

  try:
    fdoc = etree.parse(f).getroot()
    if not xmlschema.validate(fdoc):
      errors.append(identifier + ' does not follow mets standards')
  except etree.XMLSyntaxError:
    errors.append(identifier + ' is not a well-formed XML file.')
    pass

  return errors

def _validate_file_notempty(oc, identifier, file_info):
  errors = []

  file_info.seek(0, os.SEEK_END)
  size = file_info.tell()
  
  if not size:
    errors.append(identifier + ' is an empty file.')
  return errors

def validate_pdf(oc, identifier, file_info):
  """Make sure that a given .pdf file is well-formed and valid, and that the
     date element is arranged as yyyy-mm-dd. 

     Arguments:
     oc         -- an owncloud object, or None, for testing.
     identifier -- for error messages.
     file_info  -- a fileinfo object, the mmdd directory containing the struct.txt
  """
  try:
    file_object = io.BytesIO(oc.get_file_contents('{}/{}.pdf'.format(
                    file_info.path, get_identifier_from_fileinfo(oc, f))))
    return _validate_file_notempty(oc, identifier, file_object)
  except owncloud.HTTPResponseError:
    return [identifier + '.pdf does not exist.']

def validate_txt(oc, identifier, file_info):
  """Make sure that a given .txt file is well-formed and valid, and that the
     date element is arranged as yyyy-mm-dd. 

     Arguments:
     oc         -- an owncloud object, or None, for testing.
     identifier -- for error messages.
     file_info  -- a fileinfo object, the mmdd directory containing the struct.txt
  """
  try:
    file_object = io.BytesIO(oc.get_file_contents('{}/{}.txt'.format(
                    file_info.path, get_identifier_from_fileinfo(oc, f))))
    return _validate_file_notempty(oc, identifier, file_object)
  except owncloud.HTTPResponseError:
    return [identifier + '.txt does not exist.']

def validate_struct_txt(oc, identifier, file_info):
  """Make sure that a given struct.txt file is well-formed and valid, and that the
     date element is arranged as yyyy-mm-dd. 

     Arguments:
     oc         -- an owncloud object, or None, for testing.
     identifier -- for error messages.
     file_info  -- a fileinfo object, the mmdd directory containing the struct.txt
  """
  try:
    file_object = io.BytesIO(oc.get_file_contents('{}/{}.struct.txt'.format(
                    file_info.path, get_identifier_from_fileinfo(oc, f))))
    return _validate_struct_txt_file(oc, identifier, file_object)
  except owncloud.HTTPResponseError:
    return [identifier + '.struct.txt does not exist.']

def _validate_struct_txt_file(oc, identifier, f):
  """Make sure that a given struct.txt is valid. It should be tab-delimited
     data, with a header row. Each record should contains a field for object,
     page and milestone.

     Arguments:
     oc -- an owncloud object, or None, for testing.
     f  -- a file object containing a struct.txt file.
  """
  errors = []

  num_lines = sum(1 for line in f)
  f.seek(0,0)
  firstline = f.readline()
  firstlinepattern = re.compile("^object\tpage\tmilestone\n")
  if not firstlinepattern.fullmatch(firstline):
    errors.append(identifier + ' has an error in the first line.')
  currlinenum = 2
  midlinespattern = re.compile('^\d{8}\t\d\n')
  finlinepattern = re.compile('^\d{8}\t\d')
  currline = f.readline()
  while(currline):
    if not midlinespattern.fullmatch(currline):
        if not ((currlinenum == num_lines) and finlinepattern.fullmatch(currline)):
          errors.append(identifier + ' has an error in line %d.' % currlinenum)
    currlinenum += 1
    currline = f.readline()

  return errors


if __name__ == '__main__':
  """ Produce an input file for a year's worth of mvol data.
      This checks to be sure that files are available via specific URLs, and it
      produces an input file for the OCR building script. 
  """

  parser = argparse.ArgumentParser()
  parser.add_argument("username", help="WebDAV username.")
  parser.add_argument("directory", help="e.g. IIIF_Files/mvol/0004/1930/0105")
  args = parser.parse_args()

  try:
    oc = owncloud.Client(os.environ['OWNCLOUD_SERVER'])
  except KeyError:
    sys.stderr.write("OWNCLOUD_SERVER environmental variable not set.\n")
    sys.exit()

  password = getpass.getpass('WebDAV password: ')

  try:
    oc.login(args.username, password)
  except owncloud.HTTPResponseError:
    sys.stderr.write('incorrect WebDAV password.\n')
    sys.exit()

  errors = []

  try:
    f = oc.file_info(args.directory)
    identifier = get_identifier_from_fileinfo(oc, f)
    errors = errors + validate_mvol_directory(oc, identifier, f)
    errors = errors + validate_mvol_number_directory(oc, identifier, f)
    errors = errors + validate_year_directory(oc, identifier, f)
    errors = errors + validate_date_directory(oc, identifier, f)
    errors = errors + validate_alto_directory(oc, identifier, f)
    errors = errors + validate_jpeg_directory(oc, identifier, f)
    errors = errors + validate_tiff_directory(oc, identifier, f)
    errors = errors + validate_dc_xml(oc, identifier, f)
    errors = errors + validate_mets_xml(oc, identifier, f)
    errors = errors + validate_pdf(oc, identifier, f)
    errors = errors + validate_struct_txt(oc, identifier, f)
  except owncloud.HTTPResponseError:
    errors = errors + [args.directory + ' does not exist.']

  for e in errors:
    print(e)
