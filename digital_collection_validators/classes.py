import csv
import getpass
import io
import os
import owncloud
import paramiko
import re
import requests
import stat
import subprocess
import sys
from pathlib import Path 
from lxml import etree
from xml.etree import ElementTree


class DigitalCollectionValidator:
    def __init__(self):
        self.local_root = None

    def connect_to_db(self, db_path):
        self.conn = sqlite3.connect(db_path)

    def get_identifiers_from_db(self, identifier_chunk, valid_only=True):
        """Get valid and non-valid identifiers for a given identifier chunk.
        If the identifier_chunk is itself an identifier, this function
        should return a list with one element, containing that identifier
        only.

        Args:
            identifier_chunk (str): e.g., 'mvol', 'mvol-0005',
            'mvol-0005-0001', 'mvol-0005-0001-0001'

            valid_only (bool)

        Returns:
            a list of identifiers from the database.
        """
    
        c = self.conn.cursor()
        if valid_only:
            sql = 'SELECT identifier FROM validation WHERE (identifier LIKE ? OR identifier = ?) AND validation = 1'
        else:
            sql = 'SELECT identifier FROM validation WHERE (identifier LIKE ? OR identifier = ?)'

        c.execute(
            sql,
            ('{}-%'.format(identifier_chunk), identifier_chunk)
        )
        identifiers = set()
        for r in c.fetchall():
            identifiers.add(r[0])
        return sorted(list(identifiers))

    def get_identifier_chunk_children_from_db(self, identifier_chunk):
        """Get the children of a given identifier chunk. In cases where the
        children of an identifier chunk are themselves identifiers, those
        identifiers should all be valid. In cases where the children of an 
        identifier chunk are identifiers, those identifier chunks should
        each contain at least one valid child.

        Args:
            identifier_chunk (str): e.g., 'mvol', 'mvol-0005',
            'mvol-0005-0001', 'mvol-0005-0001-0001'

        Returns:
            a list of identifier chunk children, e.g. 'mvol-0001',
            'mvol-0002', 'mvol-0004', etc.

        """
    
        child_chunk_count = len(identifier_chunk.split('-')) + 1
    
        identifier_chunks = set()
        for i in self.get_identifiers_from_db(identifier_chunk):
            test_child = '-'.join(i.split('-')[:child_chunk_count])
            if len(test_child.split('-')) == child_chunk_count:
                identifier_chunks.add(test_child)
        return sorted(list(identifier_chunks))


    def set_local_root(self, local_root):
        """Set a local root for local validation

        Args:
            local_root (str): absolute path to files.
        """
        self.local_root = local_root
 

    def get_identifier_chunk(self, path):
        """Get an identifier chunk from a path to an mmdd directory.

        Args:
            path (str): to a directory on the server. 

        Returns:
            str: an identifier, e.g. 'mvol-0004-1930-0103'.
        """
        # get everything after 'IIIF_Files' in the path.
        shortened_path_chunks = re.sub('^.*IIIF_Files/', '', path).split('/')

        if shortened_path_chunks[0] in ('ewm', 'gms', 'speculum','chopin'):
            return shortened_path_chunks.pop()
        if shortened_path_chunks[0] in ('mvol',):
            return '-'.join(shortened_path_chunks[:4])
        if shortened_path_chunks[0] in ('apf'):
            return shortened_path_chunks[0] + shortened_path_chunks[1]
        else:
            raise NotImplementedError

    def get_identifier(self, path):
        """Returns identifier chunk from a path
        
        Args:
            path (str): to a directory on the server.
            
        Returns:
            str: an identifier chunk, e.g. 'mvol-0001', 'chopin-001
        """
        identifier_chunk = self.get_identifier_chunk(path)
        if self.is_identifier(identifier_chunk):
            return identifier_chunk
        else:
            raise ValueError

    def get_path(self, identifier_chunk):
        """Return the path to a given identifier chunk on owncloud's disk space.
        N.B., you should use these paths for read-only access.

        Args:
            identifier_chunk (str): e.g., 'mvol-0001', 'mvol-0001-0002-0003'

        Returns:
            str: the path to an identifier chunk on disk. 
        """

        project = self.get_project(identifier_chunk)

        if project not in ('apf', 'chopin', 'ewm', 'gms', 'mvol', 'speculum'):
            raise NotImplementedError

        # for ewm, gms, speculum, and chopin, sections of the identifier are repeated
        # in subfolders, e.g. ewm/ewm-0001
        if project in ('chopin', 'ewm', 'gms', 'speculum'):
            subfolders = []
            identifier_sections = identifier_chunk.split('-')
            for i in range(0, len(identifier_sections)):
                subfolders.append('-'.join(identifier_sections[:i+1]))

            if self.local_root:
                return self.local_root + '/'.join(subfolders)
            else:
                raise RuntimeError

        # for mvol, apf, and rac, sections of the identifier are not repeated in subfolders,
        # e.g. mvol/0001/0002/0003.
        if project in ('apf', 'mvol'):
            if self.local_root:
                return self.local_root + '/' + identifier_chunk.replace('-', '/')
            else:
                raise RuntimeError


    def get_project(self, identifier_chunk):
        """Return the first part of an identifier chunk, e.g. 'mvol'.

        Args:
            identifier_chunk (str): e.g. 'mvol-0001'

        Returns:
            str: the first part of the identifier chunk.
        """
        project = re.sub('-.*', '', identifier_chunk)
        if project in ('ewm', 'gms', 'mvol', 'speculum'):
            return project
        elif 'apf' in identifier_chunk:
            return 'apf'
        elif 'chopin' in identifier_chunk:
            return 'chopin'
        elif 'rac' in identifier_chunk or 'chess' in identifier_chunk or 'rose' in identifier_chunk:
            return 'rac'
        else:
            raise NotImplementedError

    def is_identifier(self, identifier_chunk):
        """Return true if this identifier chunk is a complete identifier. 

        Args:
            identifier_chunk (str): e.g., 'mvol-0001', 'mvol-0001-0002-0003'

        Returns:
            bool
        """
        if self.get_project(identifier_chunk) == 'ewm':
            return bool(re.match('^ewm-\d{4}$', identifier_chunk))
        elif self.get_project(identifier_chunk) == 'gms':
            return bool(re.match('^gms-\d{4}$', identifier_chunk))
        elif self.get_project(identifier_chunk) == 'mvol':
            return bool(re.match('^mvol-\d{4}-\d{4}-[0-9A-Z]{4}(-\d{2})?$', identifier_chunk))
        elif self.get_project(identifier_chunk) == 'speculum':
            return bool(re.match('^speculum-\d{4}$', identifier_chunk))
        elif self.get_project(identifier_chunk) == 'apf':
            return (bool(re.match('^apf\d{1}-\d{5}$',identifier_chunk))
                    or bool(re.match('^apf\d{1}-\d{5}-\d{3}',identifier_chunk)))
        elif self.get_project(identifier_chunk) == 'chopin':
            return bool(re.match('^chopin-\d{3}$',identifier_chunk)) 
        elif self.get_project(identifier_chunk) == 'rac':
            return (bool(re.match('^rac-\d{4}$',identifier_chunk))
                    or bool(re.match('^chess-\d{4}-\d{3}$',identifier_chunk))
                    or bool(re.match('^rose-\d{4}-\d{3}$',identifier_chunk)))
        else:
            raise NotImplementedError

    def is_identifier_chunk(self, identifier_chunk):
        """Return true if this is a valid identifier chunk.

        Args:
            identifier_chunk (str): check to see if this identifier chunk is
            valid.

        Returns:
            bool
        """
        if self.get_project(identifier_chunk) == 'ewm':
            r = '^ewm(-\d{4}(-\d{4}([A-Za-z]{2})?)?)?$'
        elif self.get_project(identifier_chunk) == 'gms':
            r = '^gms(-\d{4}(-\d{3})?)?$'
        elif self.get_project(identifier_chunk) == 'mvol':
            r = '^mvol(-\d{4}(-\d{4}(-[0-9A-Z]{4}(-\d{2})?)?)?)?$'
        elif self.get_project(identifier_chunk) == 'speculum':
            r = '^speculum(-\d{4}(-\d{3})?)?$'
        elif self.get_project(identifier_chunk) == 'apf':
            r = '^apf(\d{1}(-\d{5}(-\d{3})?)?)?$'
        elif self.get_project(identifier_chunk) == 'chopin':
            r = '^chopin(-\d{3}(-\d{3})?)?$'
        elif self.get_project(identifier_chunk) == 'rac':
            q = '^rac(-\d{4})?$'
            r = '^chess-\d{4}-\d{3}?$'
            s = '^rose-\d{4}-\d{3}?$'
            return (bool(re.match(q, identifier_chunk)) 
                    or bool(re.match(r, identifier_chunk)) 
                    or bool(re.match(s, identifier_chunk)))
        else:
            raise NotImplementedError
        return bool(re.match(r, identifier_chunk))

    def recursive_ls(self, identifier_chunk):
        """Get a list of identifiers in on disk. 

        Args:
            identifier chunk (str): e.g., 'mvol-0001', 'mvol-0001-0002-0003'

        Returns:
            list: a list of identifiers, e.g. 'mvol-0001-0002-0003'
        """
        identifiers = []
        for root, dirs, files in os.walk(self.get_path(identifier_chunk)):
            if bool(set(dirs).intersection(
                set(('jpg', 'pos', 'tif', 'ALTO', 'JPEG', 'POS', 'TIFF'))
            )):
                identifier = '-'.join(root.split(os.sep)[5:])
                if self.is_identifier(identifier):
                    identifiers.append(identifier)
        return identifiers

    def list_directory(self, identifier):
        """Get a list of files from starting identifier.

        Args:
            identifier chunk (str): e.g., 'chopin', 'speculum-0001', 'ewm-0001-0001.tif'

        Returns:
            list or single file: e.g. 'chopin-003-001.tif, chopin-003-002.tif, chopin-003-003.tif ...', 'speculum-0006-001.tif'
        """

        check_format = self.is_identifier_chunk(identifier)

        if check_format != True:
            print("File or directory doesn't exist")
            sys.exit()

        general = {
            'ewm' : 13,
            'chopin' : 14,
            'gms' : 12,
            'speculum' : 17
        }

        identifiers = []
        length = len(identifier)

        #prints all the files in all existing directories
        if identifier in general:
            dir_files = os.listdir(self.get_path(identifier))
            for chunk in dir_files:
                for folder in os.listdir(self.get_path(chunk)):
                    if '.' not in folder:
                        identifiers += os.listdir(self.get_path(chunk) + '/' + str(folder))
            return identifiers

        #prints all files in specified directory
        if 'ewm' in identifier or 'gms' in identifier:
            path = self.get_path(identifier[:8])
        elif 'chopin' in identifier:
            path = self.get_path(identifier[:10])
        elif 'speculum' in identifier:
            path = self.get_path(identifier[:13])

        dir_files = os.listdir(path)
        for folder in dir_files:
            if '.' not in folder:
                identifiers += os.listdir(path + '/' + str(folder))

        #searching for single, unique file
        if length >= general[self.get_project(identifier)]:
            for i in identifiers:
                if i[:-4] == identifier:
                    return [i]
        return identifiers


    def validate_files(self, identifier):
        """For a given identifier, make sure a TIFF file exists. Confirm
        that the file is non-empty.
        
        Args:
            identifier (str): e.g. 'speculum-0001-001', 'chopin-001-001'
        """

        if not self.is_identifier_chunk(identifier):
            print("File doesn't exist")
            sys.exit()

        if 'ewm' in identifier or 'gms' in identifier:
            path = self.get_path(identifier[:8])
        elif 'chopin' in identifier:
            path = self.get_path(identifier[:10])
        elif 'speculum' in identifier:
            path = self.get_path(identifier[:13])

        dir_files = os.listdir(path)

        for folder in dir_files:
            if '.' not in folder:
                for image in os.listdir(path + '/' + str(folder)):
                    if identifier in image:
                        path += '/' + str(folder) + '/' + str(image)
                        f = self.open(path)
                        return self._validate_file_notempty(f)
        
        return ['{}/{}.tiff missing\n'.format(self.get_path(identifier), identifier)]

    def validate_tiff_directory(self, identifier, folder_name):
        """Validates TIFF directories within an identifier.
        
        Args:
            identifier (str): e.g. 'chopin-001' 
            folder_name (str): e.g. 'TIFF' 
            
        Returns:
            pass: empty list
            fail: list with error messages
        """

        extensions = {
            'ALTO': 'xml',
            'JPEG': 'jpg',
            'POS': 'pos',
            'TIFF': 'tif'
        }

        if folder_name not in extensions:
            raise ValueError('unsupported folder name.\n')

        if not self.is_identifier(identifier):
            raise ValueError('invalid identifier.\n')

        path = self.get_path(identifier)
        folders = os.listdir(path)

        entries = []
        for directory in folders:
            if '.' not in directory:
                for entry in os.listdir(path + '/' + str(directory)):
                    entries.append(path + '/' + directory + '/' + str(entry))
        
        errors = []
        for i in entries:
            file_name = i.split('/')[-1]

            if not file_name.endswith(extensions[folder_name]):
                errors.append('%s is not a tif file' % file_name)

            f = self.open(i)
            empty = self._validate_file_notempty(f)
            if empty:
                errors.append(empty[0])
            f.close()

        return errors
                        

    def get_newest_modification_time_from_directory(self, directory):
        """ Helper function for get_newest_modification_time. Recursively searches
        subdirectories for the newest modification time. 

        Args:
            ftp: paramiko ftp instance
            directory (str): path to an identifier's files on disk, on either
            owncloud or one of the XTF servers.

        Returns:
            the newest unix timestamp present in that directory.
        """

        mtimes = []
        for entry in self.ftp.listdir_attr(directory):
            if stat.S_ISDIR(entry.st_mode):
                mtime = self.get_newest_modification_time_from_directory(
                    '{}/{}'.format(directory, entry.filename)
                )
            else:
                try:
                    mtimes.append(entry.st_mtime)
                except FileNotFoundError:
                    sys.stderr.write(directory + '\n')
                    raise FileNotFoundError

        if mtimes:
            return max(mtimes)
        else:
            return 0

    def get_newest_modification_time(self, identifier):
        return self.get_newest_modification_time_from_directory(self.get_path(identifier))

    @staticmethod
    def _validate_file_notempty(f):
        """Make sure that a given file is not empty.

        Args:
            f: a file-like object.
        """
        errors = []

        f.seek(0, os.SEEK_END)
        size = f.tell()

        if not size:
            try:
                name = f.name
                name = name.split('/')[-1]
                errors.append('%s is an empty file.\n' % name)
            except AttributeError:
                errors.append('empty file.\n')
    
        f.close()
        return errors

    def get_csv_data(self, identifier_chunk):
        """Get CSV data for a specific identifier chunk.
 
        Args:
            identifier_year (str): e.g. 'mvol-0004-1951'

        Returns:
            dict: data about these identifiers.
        """
        path = self.get_path(identifier_chunk)
        csv_data = {}
        for entry in os.listdir(path):
            if re.search('\.csv$', entry):
                f = self.ftp.file('{}/{}'.format(path, entry))
                reader = csv.reader(f)
                next(reader, None)
                try:
                    for row in reader:
                        csv_data[row[2]] = {
                            'title': row[0],
                            'date': row[1],
                            'description': row[3]
                        }
                except IndexError:
                    break
        return csv_data
    

class ApfValidator(DigitalCollectionValidator):
    def validate_tiff_files(self, identifier):
        """For a given identifier, make sure a TIFF file exists. Confirm
        that the file is non-empty.

        Args:
            identifier (str): e.g. 'apf1-00001'
        """

        path = self.get_path('apf') +  '/' + str(identifier[3])

        for image in os.listdir(path):
            if identifier in image:
                path += '/' + image
                f = self.open(path)
                return self._validate_file_notempty(f)
        
        return ['{}/{}.tiff missing\n'.format(self.get_path(identifier), identifier)]


    def validate(self, identifier):
        """Wrapper to call all validation functions. 

        Args:
            identifier (str): e.g. 'apf1-00001'
        """
        assert self.get_project(identifier) == 'apf'

        errors = []
        errors += self.validate_tiff_files(identifier)
        return errors

    def list_dir(self, identifier):
        '''
        Lists all files within given identifier 

        Args:
            identifier (str): e.g. 'apf1'
        '''

        check_format = self.is_identifier_chunk(identifier)

        if check_format == False:
            print("File or directory doesn't exist")
            sys.exit()

        path = self.get_path('apf')

        length = len(identifier)

        identifiers = []
        if length == 4 or length >= 10:
            path += '/' + identifier[3]
        elif length != 3:
            print("File doesn't exist")
        
        if identifier == 'apf':
            for directory in os.listdir(path):
                identifiers += os.listdir(path + '/' + str(directory))
            return identifiers 

        identifiers = os.listdir(path)

        fin = []
        for i in identifiers:
            if i.endswith('.tif'):
                fin.append(i)

        if length >= 10:
            for i in identifiers:
                if i[:-4] == identifier:
                    return [i]
            raise NotImplementedError
        
        return fin  


class ChopinValidator(DigitalCollectionValidator):
    def validate_tiff_files(self, identifier):
        """For a given identifier, make sure a TIFF file exists. Confirm
        that the file is non-empty.
        
        Args:
            identifier (str): e.g. 'chopin-002'
        """

        assert re.match('^chopin-\d{3}$', identifier)

        path = self.get_path(identifier) + '/tifs/'

        # regex to match filenames that look correct.
        r = '^' + identifier + '-\d{3}\.tif$'

        existing_f = set(os.listdir(path))

        # get what looks like the highest object number on disk. 
        hi_obj_num = 0
        for f in sorted(list(existing_f)):
            if re.match(r, f):
                hi_obj_num = int(f.split('.')[0].split('-')[-1])

	# build a set of expected filenames.
        expected_f = set()
        for i in range(1, hi_obj_num + 1):
            expected_f.add('{}-{}.tif'.format(identifier, str(i).zfill(3)))

        errors = []
        for f in sorted(list(expected_f.difference(existing_f))):
            errors.append('{}/tifs/{} not found.\n'.format(identifier, f))
        for f in sorted(list(existing_f.difference(expected_f))):
            errors.append('{}/tifs/{} not expected.\n'.format(identifier, f))
        return errors

    def validate(self, identifier):
        """Wrapper to call all validation functions. 

        Args:
            identifier (str): e.g. 'chopin-001-001'
        """
        assert self.get_project(identifier) == 'chopin'

        errors = []
        errors += self.validate_tiff_files(identifier)
        return errors


class EwmValidator(DigitalCollectionValidator):
    def validate(self, identifier):
        """Wrapper to call all validation functions. 

        Args:
            identifier (str): e.g. 'ewm-0001-0001'
                                   'ewm-0001-0001cr'
        """
        assert self.get_project(identifier) == 'ewm'

        errors = []
        errors += self.validate_tiff_files(identifier)
        return errors
        

class GmsValidator(DigitalCollectionValidator):
    def validate_tiff_files(self, identifier):
        """For a given identifier, make sure a TIFF file exists. Confirm
        that the file is non-empty.
        
        Args:
            identifier (str): e.g. 'gms-0019'
        """

        assert re.match('^gms-\d{4}$', identifier)

        path = self.get_path(identifier) + '/tifs/'

        # regex to match filenames that look correct.
        r = '^' + identifier + '-\d{3}\.tif$'

        existing_f = set(os.listdir(path))

        # get what looks like the highest object number on disk. 
        hi_obj_num = 0
        for f in sorted(list(existing_f)):
            if re.match(r, f):
                hi_obj_num = int(f.split('.')[0].split('-')[-1])

	# build a set of expected filenames.
        expected_f = set()
        for i in range(1, hi_obj_num + 1):
            expected_f.add('{}-{}.tif'.format(identifier, str(i).zfill(3)))

        errors = []
        for f in sorted(list(expected_f.difference(existing_f))):
            errors.append('{}/tifs/{} not found.\n'.format(identifier, f))
        for f in sorted(list(existing_f.difference(expected_f))):
            errors.append('{}/tifs/{} not expected.\n'.format(identifier, f))
        return errors

    def validate(self, identifier):
        """Wrapper to call all validation functions. 

        Args:
            identifier (str): e.g. 'gms-0019'
        """
        assert self.get_project(identifier) == 'gms'

        errors = []
        errors += self.validate_tiff_files(identifier)
        return errors


class MvolValidator(DigitalCollectionValidator):
    def validate_directory(self, identifier, folder_name):
        """A helper function to validate ALTO, JPEG, and TIFF folders inside mmdd
        folders.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'
            folder_name (str): the name of the folder: ALTO|JPEG|TIFF

        Returns:
            list: error messages, or an empty list.
        """

        assert self.get_project(identifier) == 'mvol'

        extensions = {
            'ALTO': 'xml',
            'JPEG': 'jpg',
            'POS': 'pos',
            'TIFF': 'tif'
        }

        if folder_name not in extensions.keys():
            raise ValueError('unsupported folder_name.\n')

        mmdd_path = self.get_path(identifier)

        # raise an IOError if the ALTO, JPEG, or TIFF directory does not exist.
        os.stat(mmdd_path + '/' + folder_name)

        if bool(re.search('-[0-9]{2}$', identifier)):
            filename_re = '^%s-%s-%s-%s-%s_\d{4}\.%s$' % (
                mmdd_path.split('/')[-5],
                mmdd_path.split('/')[-4],
                mmdd_path.split('/')[-3],
                mmdd_path.split('/')[-2],
                mmdd_path.split('/')[-1],
                extensions[folder_name]
            )
        else:
            filename_re = '^%s-%s-%s-%s_\d{4}\.%s$' % (
                mmdd_path.split('/')[-4],
                mmdd_path.split('/')[-3],
                mmdd_path.split('/')[-2],
                mmdd_path.split('/')[-1],
                extensions[folder_name]
            )

        entries = []
        for entry in os.listdir('{}/{}'.format(mmdd_path, folder_name)):
            if entry.endswith(extensions[folder_name]):
                entries.append(entry)
        entries.sort()

        entries_pass = []
        entries_fail = []
        for entry in entries:
            if re.match(filename_re, entry):
                if folder_name == 'ALTO':
                    with self.open('{}/ALTO/{}'.format(self.get_path(identifier), entry)) as f:
                        try:
                            ElementTree.fromstring(f.read())
                            entries_pass.append(entry)
                        except ElementTree.ParseError:
                            entries_fail.append(entry)
            else:
                entries_fail.append(entry)

        errors = []
        if entries_fail:
            for entry in entries_fail:
                errors.append(
                    '{}/{}/{} problem.\n'.format(
                        identifier,
                        folder_name,
                        entry
                    )
                )
        return errors

    def validate_alto_or_pos_directory(self, identifier):
        """Validate that an ALTO or POS folder exists. Make sure it contains appropriate
        files.

        Args:
            identifier (str): 'mvol-0001-0002-0003'

        Returns:
            list: error messages, or an empty list.
        """

        assert self.get_project(identifier) == 'mvol'

        try:
            return self.validate_directory(identifier, 'ALTO')
        except IOError:
            try:
                return self.validate_directory(identifier, 'POS')
            except IOError:
                return ['{}/ALTO or POS missing\n'.format(self.get_path(identifier))]

    def validate_jpeg_directory(self, identifier):
        """Validate that an JPEG folder exists. Make sure it contains appropriate
        files.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'

        Returns:
            list: error messages, or an empty list.
        """

        assert self.get_project(identifier) == 'mvol'

        try:
            return self.validate_directory(identifier, 'JPEG')
        except IOError:
            return ['{}/JPEG missing\n'.format(self.get_path(identifier))]

    def validate_tiff_directory(self, identifier):
        """Validate that an TIFF folder exists. Make sure it contains appropriate
        files.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'

        Returns:
            list: error messages, or an empty list.
        """

        assert self.get_project(identifier) == 'mvol'
        try:
            return self.validate_directory(identifier, 'TIFF')
        except IOError:
            return ['{}/TIFF missing\n'.format(self.get_path(identifier))]

    def validate_dc_xml(self, identifier, f=None):
        """Make sure that a given dc.xml file is well-formed and valid, and that the
        date element is arranged as yyyy-mm-dd.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'
        """

        assert self.get_project(identifier) == 'mvol'

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
            if not f:
                f = self.open('{}/{}.dc.xml'.format(
                    self.get_path(identifier),
                    identifier)
                )
            metadata = etree.parse(f)
            if not dtd.validate(metadata):
                errors.append('{}/{}.dc.xml not valid\n'.format(self.get_path(identifier), identifier))
            elif identifier.startswith('mvol-0004'):
                datepull = metadata.findtext("date")
                pattern = re.compile("^\d{4}(-\d{2})?(-\d{2})?")
                attemptmatch = pattern.fullmatch(datepull)
                if attemptmatch:
                    sections = [int(s)
                                for s in re.findall(r'\b\d+\b', datepull)]
                    length = len(sections)
                    if (sections[0] < 1700) | (sections[0] > 2100):
                        errors.append(
                            '{}/{}.dc.xml has an incorrect year field\n'.format(self.get_path(identifier), identifier))
                    if length > 1:
                        if (sections[1] < 1) | (sections[1] > 12):
                            errors.append(
                                '{}/{}.dc.xml has an incorrect month field\n'.format(self.get_path(identifier), identifier))
                    if length > 2:
                        if (sections[2] < 1) | (sections[2] > 31):
                            errors.append(
                                '{}/{}.dc.xml has an incorrect day field\n'.format(self.get_path(identifier), identifier))
                    else:
                        errors.append(
                            '{}/{}.dc.xml has an incorrect date\n'.format(self.get_path(identifier), identifier))
        except (FileNotFoundError, IOError):
            errors.append('{}/{}.dc.xml missing\n'.format(self.get_path(identifier), identifier))
            pass
        except etree.XMLSyntaxError as e:
            errors.append('{}/{}.dc.xml not well-formed\n'.format(self.get_path(identifier), identifier))
            pass

        return errors

    def validate_struct_txt(self, identifier, f=None):
        """Make sure that a given struct.txt is valid. It should be tab-delimited
        data, with a header row. Each record should contains a field for object,
        page and milestone.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'
            f: a file-like object, for testing. 
        """

        assert self.get_project(identifier) == 'mvol'

        if not f:
            try:
                f = self.open(
                    '{}/{}.struct.txt'.format(self.get_path(identifier), identifier))
            except (FileNotFoundError, IOError):
                return ['{}/{}.struct.txt missing\n'.format(self.get_path(identifier), identifier)]

        line = f.readline()
        if not re.match('^object\tpage\tmilestone', line):
            return ['{}/{}.struct.txt has one or more errors\n'.format(self.get_path(identifier), identifier)]
        line = f.readline()
        while line:
            if not re.match('^\d{8}(\t.*)?$', line):
                return ['{}/{}.struct.txt has one or more errors\n'.format(self.get_path(identifier), identifier)]
            line = f.readline()
        return []

    def validate_txt(self, identifier):
        """Make sure that a .txt file exists for an identifier.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'
        """

        assert self.get_project(identifier) == 'mvol'

        try:
            f = self.open('{}/{}.txt'.format(
                self.get_path(identifier),
                identifier))
            return DigitalCollectionValidator._validate_file_notempty(f)
        except (FileNotFoundError, IOError):
            return ['{}/{}.txt missing\n'.format(self.get_path(identifier), identifier)]

    def validate_pdf(self, identifier):
        """Make sure that a PDF exists for an identifier.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'
        """

        assert self.get_project(identifier) == 'mvol'

        try:
            f = self.open('{}/{}.pdf'.format(
                self.get_path(identifier),
                identifier))
            return DigitalCollectionValidator._validate_file_notempty(f)
        except (FileNotFoundError, IOError):
            return ['{}/{}.pdf missing\n'.format(self.get_path(identifier), identifier)]

    def validate_allowable_files_only(self, identifier):
        """
        JEJ TODO: make sure only allowable files are in the directory.
        """
        assert self.get_project(identifier) == 'mvol'

        errors = []

        allowable_files = set((
            '{}.dc.xml'.format(identifier),
            '{}.mets.xml'.format(identifier),
            '{}.pdf'.format(identifier),
            '{}.struct.txt'.format(identifier),
            '{}.txt'.format(identifier)
        ))

        files_present = set()
        for f in os.listdir('{}/{}'.format(
            self.local_root, 
            identifier.replace('-', '/')
        )):
            if os.path.isfile('{}/{}/{}'.format(
                self.local_root,
                identifier.replace('-', '/'),
                f
            )):
                files_present.add(f)

        for f in files_present.difference(allowable_files):
            errors.append('non-allowable file {} in {}\n'.format(f, identifier))

        if not os.path.isdir('{}/{}/JPEG'.format(
            self.local_root,
            identifier.replace('-', '/')
        )):
            errors.append('JPEG dir missing in {}\n'.format(identifier))

        if not os.path.isdir('{}/{}/TIFF'.format(
            self.local_root,
            identifier.replace('-', '/')
        )):
            errors.append('JPEG dir missing in {}\n'.format(identifier))

        if not os.path.isdir('{}/{}/ALTO'.format(
            self.local_root,
            identifier.replace('-', '/')
        )) and not os.path.isdir('{}/{}/POS'.format(
            self.local_root,
            identifier.replace('-', '/')
        )):
            errors.append('ALTO or POS dir missing in {}\n'.format(identifier))

        counts = {}
        for d in ('ALTO', 'POS', 'JPEG', 'TIFF'):
            directory = '{}/{}/{}'.format(
                self.local_root,
                identifier.replace('-', '/'),
                d
            )
            if os.path.isdir(directory):
                counts[d] = len(os.listdir(directory))

        if len(set(counts.values())) > 1:
            errors.append('file count mismatch in {}\n'.format(identifier))

        return errors


    def validate_ocr(self, identifier):
        """Be sure OCR conversion works for this item.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'
        """

        assert self.get_project(identifier) == 'mvol'

        with open('/dev/null', 'w') as f:
            return_code = subprocess.call([
                'python',
                '/data/s4/jej/ocr_converters/build_ia_bookreader_ocr.py',
                '--local-root={}'.format(self.local_root),
                identifier,
                '0',
                '0'
            ],
            stdout=f
        )
        if return_code == 0:
            return []
        else:
            return ['trouble with OCR on {}\n'.format(identifier)]

    def validate(self, identifier):
        """Wrapper to call all validation functions. 

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'
        """

        assert self.get_project(identifier) == 'mvol'

        errors = []
        errors += self.validate_alto_or_pos_directory(identifier)
        errors += self.validate_jpeg_directory(identifier)
        errors += self.validate_tiff_directory(identifier)
        errors += self.validate_pdf(identifier)
        errors += self.validate_struct_txt(identifier)
        errors += self.validate_txt(identifier)
        errors += self.validate_dc_xml(identifier)
        errors += self.validate_allowable_files_only(identifier)
        if not errors:
            errors += self.validate_ocr(identifier)
        return errors


class RacValidator(DigitalCollectionValidator):
    def validate_tiff_files(self, identifier):
        """For a given identifier, make sure a TIFF file exists. Confirm
        that the file is non-empty.
        
        Args:
            identifier (str): e.g. 'rose-1380-001"""

        path = self.get_path(identifier) + '/tifs/'

        for image in os.listdir(path):
            if identifier in image:
                path += image
                f = self.open(path)
                return self._validate_file_notempty(f)

        return ['{}/{}.tiff missing\n'.format(self.get_path(identifier), identifier)]
        

    def validate(self, identifier):
        """Wrapper to call all validation functions. 

        Args:
            identifier (str): e.g. 'chess-0392-001'
                                   'rose-1380-001'
        """
        assert self.get_project(identifier) == 'rac'

        errors = []
        errors += self.validate_tiff_files(identifier)
        return errors

    def list_dir(self, identifier):
        """Get a list of files from starting identifier. ('rac' directory has unique file names and structures)

        Args:
            identifier chunk (str): e.g., 'rac', 'rac-0392', 'chess-0392-0001.tif'

        Returns:
            list or single file: e.g. 'chess-0392-001.tif, chess-0392-002.tif, chess-0392-003.tif ...', 'rose-1380-001.tif'
        """

        check_format = self.is_identifier_chunk(identifier)

        if check_format == False:
            print("File or directory does not exist")
            sys.exit()

        identifiers = []

        #prints all the files in all existing directories
        if identifier == 'rac':
            path = self.get_path('rac')
            dir_files = os.listdir(path)
            for chunk in dir_files:
                path_new = path
                path_new += '/' + str(chunk)
                for folder in os.listdir(path_new):
                    identifiers += os.listdir(path_new + '/' + str(folder))
            return identifiers

        #prints all files in specified directory
        elif 'rac' in identifier:
            path = self.get_path(identifier)
            dir_files = os.listdir(path)
            for chunk in dir_files:
                identifiers += os.listdir(path + '/' + str(chunk))
            return identifiers

        #searching for single, unique file
        else:
            folder = identifier[-8:]
            folder = folder[:4]
            path = self.get_path('rac') + '/' + str(folder)
            for folder in os.listdir(path):
                identifiers += os.listdir(path + '/' + str(folder))
            for i in identifiers:
                if identifier in i:
                    return [i]


class XTFValidator(DigitalCollectionValidator):
    def __init__(self, production):
        super().__init__()
        self.production = production

    def get_path(self, identifier):
        assert self.get_project(identifier) == 'mvol'

        if self.production:
            return '/usr/local/apache-tomcat-6.0/webapps/campub/data/bookreader/{}'.format(identifier)
        else:
            return '/usr/local/apache-tomcat-6.0/webapps/xtf/data/bookreader/{}'.format(identifier)
