"""Usage:
    mvol_validator.py <identifier> ...
"""

from docopt import docopt
import csv
import getpass
import os
import paramiko
import re
import sys
import io
import requests
from lxml import etree

def get_directory(identifier):
    return '/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/{}'.format(identifier.replace('-', '/'))

def get_ancestor_fileinfo(ftp, f, n):
    """Get an ancestor owncloud.FileInfo object.
       format (18|19|20)\d{2}

       Arguments:
       ftp -- an ftp instance from Paramiko. 
       f   -- a file-like object from Paramiko. 
       n   -- ancestor number. 1 = parent, 2 = grandparent, etc.

       Returns:
       a file-like object for a directory n levels up in the filesystem.
    """

    pieces = f.get_path().split('/')
    while n:
        pieces.pop()
        n = n - 1

    return ftp.file_info('/'.join(pieces))


def get_identifier_from_fileinfo(ftp, f):
    """Get an identifier string from a fileinfo object that represents a mmdd directory.

       Arguments:
       ftp -- an ftp instance from Paramiko. 
       f   -- an owncloud.FileInfo object, or a string, a path to a directory on
              the remote server. 

       Returns:
       an identifier string, e.g. 'mvol-0004-1930-0103'.
    """
    return '-'.join(f.split('/')[-4:])


def validate_mvol_directory(ftp, identifier, f):
    """Make sure that the great-grandparent of this directory is a folder called
       'mvol'.

       Arguments:
       ftp        -- an ftp instance from Paramiko. 
       identifier -- for error messages.
       f          -- a string, a path to an an mvol mmdd directory on the
                     remote server.

       Returns:
       A list of error messages, or an empty list.
    """
    
    if re.search('mvol/\d{4}/\d{4}/\d{4}$', f):
        return []
    else:
        return [
            identifier +
            ' is contained in a great-grandparent folder that is not called "mvol".\n']


def validate_mvol_number_directory(ftp, identifier, f):
    """Make sure that the grandparent of this directory is a four-digit mvol
       number, in the format /d{4}.

       Arguments:
       ftp        -- an ftp instance from Paramiko. 
       identifier -- for error messages.
       f          -- a string, a path to an mvol mmdd directory on the remote
                     server.

       Returns:
       A list of error messages, or an empty list.
    """

    mvol_number_dir_str = f.split('/')[-3]
    if re.match('^\d{4}$', mvol_number_dir_str):
        return []
    else:
        return [
            identifier +
            ' is contained in a grandparent folder that is not a valid mvol number.\n']


def validate_year_directory(ftp, identifier, f):
    """Make sure that the parent of this directory is a year folder, in the
       format (18|19|20)\d{2}, for mvol-0004.

       Arguments:
       ftp        -- an ftp instance from Paramiko. 
       identifier -- for error messages.
       f          -- a string, a path to an mvol mmdd directory on the remote
                     server.

       Returns:
       A list of error messages, or an empty list.
    """
    
    if not identifier.startswith('mvol-0004'):
        return []

    mvol_year_dir_str = f.split('/')[-2]
    if re.match('^(18|19|20)\d{2}$', mvol_year_dir_str):
        return []
    else:
        return [
            identifier +
            ' is contained in a parent folder that is not a valid year.\n']


def validate_date_directory(ftp, identifier, f):
    """Make sure that this folder is in the format (0\d|1[012])[0123]\d,
       for mvol-0004.

       Arguments:
       ftp        -- an ftp instance from Paramiko. 
       identifier -- for error messages.
       f          -- a string, a path to an mvol mmdd directory on the remote
                     server.

       Returns:
       A list of error messages, or an empty list.
    """

    if not identifier.startswith('mvol-0004'):
        return []

    date_dir_str = f.split('/')[-1]
    if re.match('^(0\d|1[012])[0123]\d$', date_dir_str):
        return []
    else:
        return [identifier + ' is not a valid mmdd folder name.\n']


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


def validate_directory(ftp, identifier, f, folder_name):
    """A helper function to validate ALTO, JPEG, and TIFF folders inside mmdd
       folders.

       Arguments:
       ftp         -- an ftp object from Paramiko.
       identifier  -- for error messages.
       f           -- a (string) path to an mmdd directory (the parent of the
		      ALTO, JPEG, or TIFF directory being validated) on the
                      remote server.
       folder_name -- the name of the folder: ALTO|JPEG|TIFF

       Returns:
       A list of error messages, or an empty list.
    """

    extensions = {
        'ALTO': 'xml',
        'JPEG': 'jpg',
        'TIFF': 'tif'
    }

    if folder_name not in extensions.keys():
        raise ValueError('unsupported folder_name.\n')

    errors = []

    # raise an IOError if the ALTO, JPEG, or TIFF directory does not exist. 
    ftp.stat(f + '/' + folder_name)

    filename_re = '^%s-%s-%s-%s_\d{4}\.%s$' % (
        f.split('/')[-4],
        f.split('/')[-3],
        f.split('/')[-2],
        f.split('/')[-1],
        extensions[folder_name]
    )

    for entry in ftp.listdir(f + '/' + folder_name):
        if not re.match(filename_re, entry):
            errors.append(
                identifier + 
                '/' +
                folder_name +
                ' contains incorrectly named files.\n')
    return errors


def validate_alto_or_pos_directory(ftp, identifier, f):
    """Validate that an ALTO or POS folder exists. Make sure it contains appropriate
       files.

       Arguments:
       ftp         -- an ftp instance from Paramiko. 
       identifier  -- for error messages.
       f           -- a string, a path to an mmdd directory on the remote
		      server (the parent of the directory being validated.)

       Returns:
       A list of error messages, or an empty list.
    """
    try:
        return validate_directory(ftp, identifier, f, 'ALTO')
    except IOError:
        try:
            return validate_directory(ftp, identifier, f, 'POS')
        except IOError:
            return [identifier + ' does not contain a ALTO or POS folder.\n']


def validate_jpeg_directory(ftp, identifier, f):
    """Validate that an JPEG folder exists. Make sure it contains appropriate
       files.

       Arguments:
       ftp         -- an ftp instance from Paramiko. 
       identifier  -- for error messages.
       f           -- a string, a path to an mmdd directory on the remote
		      server that contains the directory being validated.)

       Returns:
       A list of error messages, or an empty list.
    """
    return validate_directory(ftp, identifier, f, 'JPEG')


def validate_tiff_directory(ftp, identifier, f):
    """Validate that an TIFF folder exists. Make sure it contains appropriate
       files.

       Arguments:
       ftp         -- an ftp instance from Paramiko. 
       identifier  -- for error messages.
       f           -- a string, a path to an mmdd directory (the parent
                      of the directory being validated.)

       Returns:
       A list of error messages, or an empty list.
    """
    return validate_directory(ftp, identifier, f, 'TIFF')


def _validate_dc_xml_file(ftp, identifier, file_object):
    """Make sure that a given dc.xml file is well-formed and valid, and that the
       date element is arranged as yyyy-mm-dd.

       Arguments:
       ftp         -- an ftp instance from Paramiko. 
       identifier  -- for error messages.
       file_object -- an owncloud or BytesIO file object, the .dc.xml file.
    """
    dtdf = io.StringIO(      
        """<!ELEMENT metadata ((date, description, identifier, title)|
                    (date, description, title, identifier)|
                    (date, identifier, description, title)|
                    (date, identifier, title, description)|
                    (date, title, description, identifier)|
                    (date, title, identifier, description)|
                    (description, date, identifier, title)|
                    (description, date, title, identifier)|
                    (description, identifier, date, title)|
                    (description, identifier, title, date)|
                    (description, title, date, identifier)|
                    (description, title, identifier, date)|
                    (identifier, date, description, title)|
                    (identifier, date, title, description)|
                    (identifier, description, date, title)|
                    (identifier, description, title, date)|
                    (identifier, title, date, description)|
                    (identifier, title, description, date)|
                    (title, date, description, identifier)|
                    (title, date, identifier, description)|
                    (title, description, date, identifier)|
                    (title, description, identifier, date)|
                    (title, identifier, date, description)|
                    (title, identifier, description, date))>
                    <!ELEMENT title (#PCDATA)>
                    <!ELEMENT date (#PCDATA)>
                    <!ELEMENT identifier (#PCDATA)>
                    <!ELEMENT description (#PCDATA)>
                    """)
    dtd = etree.DTD(dtdf)
    dtdf.close()
    errors = []

    try:
        metadata = etree.fromstring(file_object.read())
        if not dtd.validate(metadata):
            errors.append(identifier + '.dc.xml is not valid.\n')
        else:
            datepull = etree.ElementTree(metadata).findtext("date")
            pattern = re.compile("^\d{4}(-\d{2})?(-\d{2})?")
            attemptmatch = pattern.fullmatch(datepull)
            if attemptmatch:
                sections = [int(s) for s in re.findall(r'\b\d+\b', datepull)]
                length = len(sections) 
                if (sections[0] < 1700) | (sections[0] > 2100):
                    errors.append(
                        identifier + '.dc.xml has an incorrect year field.\n')
                if length > 1:  
                  if (sections[1] < 1) | (sections[1] > 12):
                      errors.append(identifier +
                                    '.dc.xml has an incorrect month field.\n')
                if length > 2:  
                  if (sections[2] < 1) | (sections[2] > 31):
                      errors.append(
                          identifier + '.dc.xml has an incorrect day field.\n')
            else:
                errors.append(identifier +
                              '.dc.xml has a date with a wrong format.\n')
    except etree.XMLSyntaxError as e:
        errors.append(identifier + '.dc.xml is not well-formed.\n')
        pass

    return errors


def validate_dc_xml(ftp, identifier, f):
    """Make sure that a given dc.xml file is well-formed and valid, and that the
       date element is arranged as yyyy-mm-dd.

       Arguments:
       ftp        -- an ftp instance from Paramiko. 
       identifier -- for error messages.
       f          -- a string, the path to the mmdd directory containing the
                     .dc.xml file.
    """
    try:
        in_memory_file = io.BytesIO()
        ftp.getfo('{}/{}.dc.xml'.format(f, identifier), in_memory_file)
        in_memory_file.seek(0)
        return _validate_dc_xml_file(ftp, identifier, in_memory_file)
    except FileNotFoundError:
        return [identifier + '.dc.xml does not exist.\n']


def validate_mets_xml(ftp, identifier, f):
    """Make sure that a given mets.xml file is well-formed and valid, and that the
       date element is arranged as yyyy-mm-dd.

       Arguments:
       ftp        -- an ftp instance from Paramiko. 
       identifier -- for error messages.
       f          -- a string, the path to the mmdd directory containing the
                     .mets.xml
    """
    try:
        in_memory_file = io.BytesIO()
        print('{}/{}.mets.xml'.format(f, identifier))
        sys.exit()
        ftp.getfo('{}/{}.mets.xml'.format(f, identifier), in_memory_file)
        in_memory_file.seek(0)
        return _validate_mets_xml_file(ftp, identifier, in_memory_file)
    except FileNotFoundError:
        return [identifier + '.mets.xml does not exist.\n']


def _validate_mets_xml_file(ftp, identifier, file_object):
    """Make sure that a given mets file is well-formed and valid.

       Arguments:
       ftp         -- an ftp instance from Paramiko. 
       identifier  -- for error messages.
       file_object -- a file object containing a mets.xml file.
    """
    errors = []

    # alternatively StringIO
    schemfd = open("mets.xsd.xml", 'r', encoding='utf8')
    schemdoc = etree.parse(schemfd)
    schemfd.close()
    xmlschema = etree.XMLSchema(schemdoc)

    try:
        fdoc = etree.parse(file_object).getroot()
        if not xmlschema.validate(fdoc):
            errors.append(
                identifier +
                '.mets.xml does not validate against schema.\n')
    except etree.XMLSyntaxError:
        errors.append(identifier + '.mets.xml is not a well-formed XML file.\n')
        pass

    return errors


def _validate_file_notempty(ftp, identifier, file_object, file_format):
    """Make sure that a given file is not empty.

       Arguments:
       ftp         -- an ftp instance from Paramiko. 
       identifier  -- for error messages.
       file_object -- a file object containing a mets.xml file.
       file_format -- .pdf, .struct.txt etc
    """
    errors = []

    file_object.seek(0, os.SEEK_END)
    size = file_object.tell()

    if not size:
        errors.append(identifier + file_format + ' is an empty file.\n')
    return errors


def validate_struct_txt(ftp, identifier, f):
    """Make sure that a given struct.txt file is well-formed and valid, and that the
       date element is arranged as yyyy-mm-dd.

       Arguments:
       ftp        -- an ftp instance from Paramiko. 
       identifier -- for error messages.
       f          -- a string, the path to the mmdd directory containing the
                     struct.txt
    """
    try: 
        in_memory_file = io.BytesIO()
        ftp.getfo('{}/{}.struct.txt'.format(f, identifier), in_memory_file)
        in_memory_file.seek(0)
        return _validate_struct_txt_file(ftp, identifier, in_memory_file)
    except FileNotFoundError:
        return [identifier + '.struct.txt does not exist.\n']


def _validate_struct_txt_file(ftp, identifier, file_object):
    """Make sure that a given struct.txt is valid. It should be tab-delimited
       data, with a header row. Each record should contains a field for object,
       page and milestone.

       Arguments:
       ftp         -- an ftp instance from Paramiko. 
       identifier  -- for error messages.
       file_object -- a file object containing a struct.txt file.
    """
    errors = []

    num_lines = sum(1 for line in file_object)
    firstlinepattern = re.compile("^object\tpage\tmilestone\n")
    midlinespattern = re.compile('^\d{8}\t\d\n?')
    for line in file_object:
        if not firstlinepattern.fullmatch(line) and not midlinepattern.fullmatch(line):
            errors.append(identifier + '.struct.txt has an error.')
    return errors
    

def finalcheck(directory):
    """Make sure that a passing directory does not ultimately fail validation
      for an unknown reason

       Arguments:
       directory --- name of the mvol folder being tested
    """
    freshdirectorypieces = directory.split("/")
    freshdirectorypieces.pop(0)
    freshdirectory = '-'.join(freshdirectorypieces)
    if freshdirectory[-1] == "-":
      freshdirectory = freshdirectory[:-1]
    print(freshdirectory)
    url = "https://digcollretriever.lib.uchicago.edu/projects/" + \
        freshdirectory + "/ocr?jpg_width=0&jpg_height=0&min_year=0&max_year=0"
    r = requests.get(url)
    if r.status_code != 200:
        return [directory + ' has an unknown error.\n']
    else:
        try:
            fdoc = etree.fromstring(r.content)
            return []
        except Exception:
            return [directory + ' has an unknown error.\n']


def mainvalidate(oc, directory):
    errors = []
    try:
        f = oc.file_info(directory)
        identifier = get_identifier_from_fileinfo(oc, f)
        errors = errors + validate_mvol_directory(oc, identifier, f)
        errors = errors + validate_mvol_number_directory(oc, identifier, f)
        if re.match('IIIF_Files/mvol/0004/', directory):
          errors = errors + validate_year_directory(oc, identifier, f)
          errors = errors + validate_date_directory(oc, identifier, f)
        errors = errors + validate_alto_or_pos_directory(oc, identifier, f)
        errors = errors + validate_jpeg_directory(oc, identifier, f)
        errors = errors + validate_tiff_directory(oc, identifier, f)
        #errors = errors + validate_dc_xml(oc, identifier, f)
        errors = errors + validate_mets_xml(oc, identifier, f)
        errors = errors + validate_pdf(oc, identifier, f)
        errors = errors + validate_struct_txt(oc, identifier, f)
        if not errors:
            errors = finalcheck(directory)
    except owncloud.HTTPResponseError:
        errors = errors + [directory + ' does not exist.\n']

    return errors


if __name__ == '__main__':
  """ Produce an input file for a year's worth of mvol data.
      This checks to be sure that files are available via specific URLs, and it
      produces an input file for the OCR building script. 
  """

  args = docopt(__doc__)

  password = getpass.getpass('SSH password or passphrase: ')

  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect('s3.lib.uchicago.edu', username='', password=password)
  ftp = ssh.open_sftp()

  errors = []
  for identifier in args['<identifier>']:
    directory = get_directory(identifier)
    errors = errors + validate_mvol_directory(ftp, identifier, directory)
    errors = errors + validate_mvol_number_directory(ftp, identifier, directory)
    errors = errors + validate_year_directory(ftp, identifier, directory)
    errors = errors + validate_date_directory(ftp, identifier, directory)
    errors = errors + validate_alto_or_pos_directory(ftp, identifier, directory)
    errors = errors + validate_jpeg_directory(ftp, identifier, directory)
    #errors = errors + validate_tiff_directory(ftp, identifier, directory)
    errors = errors + validate_dc_xml(ftp, identifier, directory)
    #errors = errors + validate_mets_xml(ftp, identifier, directory)
    errors = errors + validate_struct_txt(ftp, identifier, directory)

  for e in errors:
    sys.stdout.write(e + '\n')
