import csv
import io
import os
import owncloud
import paramiko
import re
import requests
import stat
import sys
from pathlib import Path 

from lxml import etree


class DigitalCollectionValidator:
    connected = 0 #variable that determines if SSH connection is made or not --> default set to 0

    def connect(self, ssh_server, paramiko_kwargs):
        """Connects user to owncloud server
        
        Args:
            ssh-server (str): name of ssh server, e.g. 's3.lib.uchicago.edu'

        Returns:
            Returns no physical attribute, only establishes ssh connection 
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('s3.lib.uchicago.edu', username='ksong814')
        self.ftp = ssh.open_sftp()
        self.connected = 1
 

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
        ids = ['ewm','gms','speculum','chopin','mvol','apf','rac']
        if project not in ids:
            raise NotImplementedError

        # for ewm, gms, speculum, and chopin, sections of the identifier are repeated
        # in subfolders, e.g. ewm/ewm-0001
        if project in ('ewm', 'gms', 'speculum', 'chopin'):
            subfolders = []
            identifier_sections = identifier_chunk.split('-')
            for i in range(0, len(identifier_sections)):
                subfolders.append('-'.join(identifier_sections[:i+1]))

            r = '/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/{}'.format(
                '/'.join(subfolders))

            if self.connected == 1:
                return r
            else:
                local = 'C:/Users/ksong814/Desktop/' # ENTER YOUR LOCAL PATH HERE
                return (local + r[60:])

        # for mvol, apf, and rac, sections of the identifier are not repeated in subfolders,
        # e.g. mvol/0001/0002/0003.
        if project in ('mvol','apf','rac'):
            if ('rac' in project) and ('rac' not in identifier_chunk):
                if self.is_identifier(identifier_chunk):
                    #isolating directory number for chess/rose file
                    if 'chess' in identifier_chunk:
                        folder = '0392'
                    elif 'rose' in identifier_chunk:
                        folder = '1380'
                    r = '/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/rac/' + folder
                else:
                    raise NotImplementedError
            else:
                r = '/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/{}'.format(identifier_chunk.replace('-', '/'))

            if self.connected == 1:
                return r
            else:
                local = 'C:/Users/ksong814/Desktop/' # ENTER YOUR LOCAL PATH HERE
                return (local + r[60:])
        else:
            raise NotImplementedError


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
            return bool(re.match('^mvol-\d{4}-\d{4}-\d{4}$', identifier_chunk))
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
            r = '^mvol(-\d{4}(-\d{4}(-\d{4})?)?)?$'
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
        if self.is_identifier(identifier_chunk):
            return [identifier_chunk]
        else:
            identifiers = []
            path = self.get_path(identifier_chunk)
            try:
                for entry in self.cs_listdir(path):
                    entry_identifier_chunk = self.get_identifier_chunk(
                        '{}/{}'.format(path, entry)
                    )
                    if self.is_identifier_chunk(entry_identifier_chunk):
                        identifiers = identifiers + \
                            self.recursive_ls(entry_identifier_chunk)
            except FileNotFoundError:
                return []
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
            dir_files = self.cs_listdir(self.get_path(identifier))
            for chunk in dir_files:
                for folder in self.cs_listdir(self.get_path(chunk)):
                    if '.' not in folder:
                        identifiers += self.cs_listdir(self.get_path(chunk) + '/' + str(folder))
            return identifiers

        #prints all files in specified directory
        if 'ewm' in identifier or 'gms' in identifier:
            path = self.get_path(identifier[:8])
        elif 'chopin' in identifier:
            path = self.get_path(identifier[:10])
        elif 'speculum' in identifier:
            path = self.get_path(identifier[:13])

        dir_files = self.cs_listdir(path)
        for folder in dir_files:
            if '.' not in folder:
                identifiers += self.cs_listdir(path + '/' + str(folder))

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

        dir_files = self.cs_listdir(path)

        for folder in dir_files:
            if '.' not in folder:
                for image in self.cs_listdir(path + '/' + str(folder)):
                    if identifier in image:
                        path += '/' + str(folder) + '/' + str(image)
                        f = self.cs_open(path)
                        return self._validate_file_notempty(f)
        
        return ['{}/{}.tiff missing\n'.format(self.get_path(identifier), identifier)]
                        

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
                errors.append('{} is an empty file.\n'.format(f.name))
            except AttributeError:
                errors.append('empty file.\n')
    
        f.close()
        return errors

    def cs_listdir(self, path):
        """Lists contents of specified directory in current server (Owncloud vs Local)

        Args:
            path (str): to a directory
        """
        if self.connected == 1:
            return self.ftp.listdir(path)
        else:
            return os.listdir(path)

    def cs_stat(self, path):
        """Performs stat() system call on specified path in current server (Owncloud vs Local)

        Args:
            path (str): to a directory
        """
        if self.connected == 1:
            return self.ftp.stat(path)
        else:
            return os.stat(path, 'r')

    def cs_open(self, path):
        """Opens a file to read or write on specified path in current server (Owncloud vs Local)

        Args:
            path (str): to a file
        """
        if self.connected == 1:
            return self.ftp.open(path)
        else:
            return open(path)

    def get_csv_data(self, identifier_chunk):
        """Get CSV data for a specific identifier chunk.
 
        Args:
            identifier_year (str): e.g. 'mvol-0004-1951'

        Returns:
            dict: data about these identifiers.
        """
        path = self.get_path(identifier_chunk)
        csv_data = {}
        for entry in self.cs_listdir(path):
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
    

class RacValidator(DigitalCollectionValidator):
    def validate_tiff_files(self, identifier):
        """For a given identifier, make sure a TIFF file exists. Confirm
        that the file is non-empty.
        
        Args:
            identifier (str): e.g. 'rose-1380-001"""

        path = self.get_path(identifier) + '/tifs/'

        for image in self.cs_listdir(path):
            if identifier in image:
                path += image
                f = self.cs_open(path)
                return self._validate_file_notempty(f)

        return ['{}/{}.tiff missing\n'.format(self.get_path(identifier), identifier)]
        

    '''
    def validate_tiff_files(self, identifier):
        """For a given identifier, make sure a TIFF file exists. Confirm
        that the file is non-empty.

        Args:
            identifier (str): e.g. 'ewm-0001-0001'
                                   'ewm-0001-0001cr
        """

        path = self.get_path(identifier) + '/tifs/'

        for image in self.cs_listdir(path):
            if identifier in image:
                path += image
                break

        print(path)

        try:
            f = self.cs_open(path)
            return SSH._validate_file_notempty(f)
        except:
            return ['{}/{}.tiff missing\n'.format(self.get_path(identifier), identifier)]
    '''

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
            dir_files = self.cs_listdir(path)
            for chunk in dir_files:
                path_new = path
                path_new += '/' + str(chunk)
                for folder in self.cs_listdir(path_new):
                    identifiers += self.cs_listdir(path_new + '/' + str(folder))
            return identifiers

        #prints all files in specified directory
        elif 'rac' in identifier:
            path = self.get_path(identifier)
            dir_files = self.cs_listdir(path)
            for chunk in dir_files:
                identifiers += self.cs_listdir(path + '/' + str(chunk))
            return identifiers

        #searching for single, unique file
        else:
            folder = identifier[-8:]
            folder = folder[:4]
            path = self.get_path('rac') + '/' + str(folder)
            for folder in self.cs_listdir(path):
                identifiers += self.cs_listdir(path + '/' + str(folder))
            for i in identifiers:
                if identifier in i:
                    return [i]


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
        

class ChopinValidator(DigitalCollectionValidator):
    def validate(self, identifier):
        """Wrapper to call all validation functions. 

        Args:
            identifier (str): e.g. 'chopin-001-001'
        """
        assert self.get_project(identifier) == 'chopin'

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
        self.cs_stat(mmdd_path + '/' + folder_name)

        filename_re = '^%s-%s-%s-%s_\d{4}\.%s$' % (
            mmdd_path.split('/')[-4],
            mmdd_path.split('/')[-3],
            mmdd_path.split('/')[-2],
            mmdd_path.split('/')[-1],
            extensions[folder_name]
        )

        entries = []
        for entry in self.cs_listdir('{}/{}'.format(mmdd_path, folder_name)):
            if entry.endswith(extensions[folder_name]):
                entries.append(entry)
        entries.sort()

        entries_pass = []
        entries_fail = []
        for entry in entries:
            if re.match(filename_re, entry):
                entries_pass.append(entry)
            else:
                entries_fail.append(entry)

        errors = []
        if entries_fail:
            if entries_pass:
                # if failed entries and passing entries both exist, don't
                # recommend filename changes to avoid collisions.
                for entry in entries_fail:
                    errors.append(
                        '{}/{}/{} should match {}\n'.format(
                            identifier,
                            folder_name,
                            entry,
                            filename_re
                        )
                    )
            else:
                for i in range(len(entries_fail)): 
                    errors.append(
                        '{}/{}/{}/{} rename to {}_{:04}.{}\n'.format(
                            self.get_path(identifier),
                            identifier,
                            folder_name,
                            entries_fail[i],
                            identifier,
                            i + 1,
                            extensions[folder_name]
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
                f = self.ftp.file('{}/{}.dc.xml'.format(
                    self.get_path(identifier),
                    identifier)
                )
            metadata = etree.parse(f)
            if not dtd.validate(metadata):
                errors.append('{}/{}.dc.xml not valid\n'.format(self.get_path(identifier), identifier))
            else:
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

    def validate_mets_xml(self, identifier, f=None):
        """Make sure that a given mets file is well-formed and valid.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'
        """

        assert self.get_project(identifier) == 'mvol'

        errors = []

        schemfd = open('{}/mets.xsd'.format(os.path.dirname(__file__)), 'r', encoding='utf8')
        schemdoc = etree.parse(schemfd)
        schemfd.close()
        xmlschema = etree.XMLSchema(schemdoc)

        if not f:
            try:
                f = self.ftp.file('{}/{}.mets.xml'.format(
                    self.get_path(identifier),
                    identifier)
                )
            except (FileNotFoundError, IOError):
                errors.append('{}/{}.mets.xml missing\n'.format(self.get_path(identifier), identifier))
                pass

        try:
            fdoc = etree.parse(f)
            if not xmlschema.validate(fdoc):
                errors.append(
                    '{}/{}.mets.xml invalid\n'.format(self.get_path(identifier), identifier)
                )
        except etree.XMLSyntaxError:
            errors.append(
                '{}/{}.mets.xml not well-formed\n'.format(self.get_path(identifier), identifier)
            )
            pass
        except TypeError:
            errors.append(
                '{}/{}.mets.xml problem\n'.format(self.get_path(identifier), identifier)
            )
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
                f = self.ftp.open(
                    '{}/{}.struct.txt'.format(self.get_path(identifier), identifier))
            except (FileNotFoundError, IOError):
                return ['{}/{}.struct.txt missing\n'.format(self.get_path(identifier), identifier)]

        line = f.readline()
        if not re.match('^object\tpage\tmilestone', line):
            return ['{}/{}.struct.txt has one or more errors'.format(self.get_path(identifier), identifier)]
        line = f.readline()
        while line:
            if not re.match('^\d{8}\t\d+', line):
                return ['{}/{}.struct.txt has one or more errors'.format(self.get_path(identifier), identifier)]
            line = f.readline()
        return []

    def validate_txt(self, identifier):
        """Make sure that a .txt file exists for an identifier.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'
        """

        assert self.get_project(identifier) == 'mvol'

        try:
            f = self.ftp.open('{}/{}.txt'.format(
                self.get_path(identifier),
                identifier))
            return SSH._validate_file_notempty(f)
        except (FileNotFoundError, IOError):
            return ['{}/{}.txt missing\n'.format(self.get_path(identifier), identifier)]

    def validate_pdf(self, identifier):
        """Make sure that a PDF exists for an identifier.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'
        """

        assert self.get_project(identifier) == 'mvol'

        try:
            f = self.ftp.open('{}/{}.pdf'.format(
                self.get_path(identifier),
                identifier))
            return SSH._validate_file_notempty(f)
        except (FileNotFoundError, IOError):
            return ['{}/{}.pdf missing\n'.format(self.get_path(identifier), identifier)]

    def finalcheck(self, identifier):
        """Make sure that a passing directory does not ultimately fail validation
        for an unknown reason

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'
        """

        assert self.get_project(identifier) == 'mvol'

        url = "https://digcollretriever.lib.uchicago.edu/projects/" + \
            identifier + "/ocr?jpg_width=0&jpg_height=0&min_year=0&max_year=0"
        r = requests.get(url)
        if r.status_code != 200:
            return ['{} contains an unknown error\n'.format(self.get_path(identifier))]
        else:
            try:
                fdoc = etree.fromstring(r.content)
                return []
            except Exception:
                return ['{} contains an unknown error.\n'.format(self.get_path(identifier))]

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
        errors += self.validate_mets_xml(identifier)
        errors += self.validate_pdf(identifier)
        errors += self.validate_struct_txt(identifier)
        errors += self.validate_txt(identifier)
        errors += self.validate_dc_xml(identifier)
        if not errors:
            errors = self.finalcheck(identifier)
        return errors


class ApfValidator(DigitalCollectionValidator):
    def validate_tiff_files(self, identifier):
        """For a given identifier, make sure a TIFF file exists. Confirm
        that the file is non-empty.

        Args:
            identifier (str): e.g. 'apf1-00001'
        """

        path = self.get_path('apf') +  '/' + str(identifier[3])

        for image in self.cs_listdir(path):
            if identifier in image:
                path += '/' + image
                f = self.cs_open(path)
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
            for directory in self.cs_listdir(path):
                identifiers += self.cs_listdir(path + '/' + str(directory))
            return identifiers 

        identifiers = self.cs_listdir(path)

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


class OwnCloudWebDAV:
    def __init__(self, server, user, password):
        self.oc = owncloud.Client(server)
        self.oc.login(user, password)

    @staticmethod
    def get_path(identifier):
        """Return a path for a given identifier on owncloud.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'

        Returns:
            str: the path to this file on owncloud.
        """

        return '/IIIF_Files/{}'.format(identifier.replace('-', '/'))

    @staticmethod
    def get_identifier(self, path):
        """Return an identifier for a given owncloud path. 

        Args:
            identifier (str): e.g. 'IIIF_Files/mvol/0001/0002/0003/ALTO/0001.xml'

        Returns:
            str: an identifier, e.g. 'mvol-0001-0002-0003'
        """

        m = re.search(path, 'IIIF_Files/(mvol)/(\d{4})/(\d{4})/(\d{4})/')
        return '{}-{}-{}-{}'.format(m.group(1), m.group(2), m.group(3), m.group(4))

    def regularize_mvol_file(self, identifier, extension):
        """Regularize METS, PDF, .txt or .struct.txt filenames. 

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'
            extension (str): e.g. '.mets.xml'
        """

        assert identifier.split('-')[0] == 'mvol'

        mvol_dir_path = self.get_path(identifier)
        mvol_file_paths = []
        for f in self.oc.list(mvol_dir_path):
            if extension == '.txt':
                if f.path.endswith('.txt') and not f.path.endswith('.struct.txt'):
                    mvol_file_paths.append(f.path)
            else:
                if f.path.endswith(extension):
                    mvol_file_paths.append(f.path)

        if len(mvol_file_paths) == 0 or len(mvol_file_paths) > 1:
            raise RuntimeError

        self.oc.move(
            mvol_file_paths[0],
            '{}/{}{}'.format(mvol_dir_path, identifier, extension)
        )

    def batch_rename(self, directory, pattern_fun):
        """Rename files in a directory (e.g. ALTO, JPEG, TIFF, etc.)
        according to a pattern. 

        Args:
        directory (str): e.g. 'IIIF_Files/mvol/0001/0002/0003/ALTO/'
        pattern_fun: a pattern function. 
        """

        source_paths = [f.path for f in self.oc.list(directory)]
        target_paths = []
        for i, s in enumerate(source_paths, 1):
            target_paths.append(pattern_fun(i, s))

        if set(source_paths).intersection(set(target_paths)):
            raise RuntimeError

        for i in range(len(source_paths)):
            self.oc.move(source_paths[i], target_paths[i])
            i = i + 1

    def put_dc_xml(self, identifier):
        """Add a dc.xml file to the given mvol directory.
        according to a pattern. 

        Args:
            identifier (str): e.g., 'mvol-0001-0002-0003'
        """

        assert identifier.split('-')[0] == 'mvol'

        remote_path = '{}/{}.dc.xml'.format(
            OwnCloudWebDAV.get_path(identifier), identifier)

        xml_data = "<?xml version='1.0' encoding='utf8'?><metadata><title>{}</title><date>{}</date><description>{}</description><identifier>{}</identifier></metadata>".format(
            OwnCloudWebDAV.get_dc_title(identifier),
            OwnCloudWebDAV.get_dc_date(identifier),
            OwnCloudWebDAV.get_dc_description(identifier),
            identifier
        )
        self.oc.put_file_contents(remote_path, xml_data)

    @staticmethod
    def get_dc_title(identifier):
        """Return the title for a given identifier.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'

        Returns:
            str: the title for an identifier chunk like 'mvol-0004'.
        """

        identifier_chunk = '-'.join(identifier.split('-')[:2])
        titles = {
            'mvol-0004': 'Daily Maroon',
        }
        return titles[identifier_chunk]

    @staticmethod
    def get_dc_description(identifier):
        """Return the description for a given identifier.

        Args:
            identifier (str): e.g. 'mvol-0001-0002-0003'

        Returns:
            str: the description for an identifier chunk like 'mvol-0004'.
        """

        identifier_chunk = '-'.join(identifier.split('-')[:2])
        descriptions = {
            'mvol-0004': 'A newspaper produced by students of the University of Chicago. Published 1902-1942 and continued by the Chicago Maroon.'
        }
        return descriptions[identifier_chunk]

    @staticmethod
    def get_dc_date(identifier):
        """Return the date for a given identifier.

        Args:
            identifier (str): e.g. 'mvol-0004-1938-0103'

        Returns:
            str: a string, e.g. '1938-01-03'
        """

        if re.search('^mvol-0004-\d{4}-\d{4}$', identifier):
            return '{}-{}-{}'.format(
                identifier.split('-')[-2],
                identifier.split('-')[-1][:2],
                identifier.split('-')[-1][2:]
            )
        else:
            raise ValueError

    @staticmethod
    def get_mvol_numbered_filename(index, path):
        """Pattern function for rename_files_owncloud, for mvol ALTO, JPEG, or TIFF
        directories. 

        Args:
            index (int): the index of this file, e.g. 1, 2, etc. 
            path str): e.g., 'IIIF_Files/mvol/0001/0002/0003/ALTO/'

        Returns:
            a correctly named file, e.g. 'mvol-0001-0002-0003_0001.xml'
        """
        extensions = {
            'ALTO': 'xml',
            'JPEG': 'jpg',
            'POS': 'pos',
            'TIFF': 'tif'
        }
        matches = re.search(
            '^/IIIF_Files/(mvol)/(\d{4})/(\d{4})/(\d{4})/(ALTO|JPEG|POS|TIFF)', path)
        return '/IIIF_Files/{}/{}/{}/{}/{}/{}-{}-{}-{}_{:04}.{}'.format(
            matches.group(1),
            matches.group(2),
            matches.group(3),
            matches.group(4),
            matches.group(5),
            matches.group(1),
            matches.group(2),
            matches.group(3),
            matches.group(4),
            index,
            extensions[matches.group(5)])
