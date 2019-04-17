import csv
import io
import os
import owncloud
import paramiko
import re
import requests
import sys

from lxml import etree


class SSH:
    def connect(self, ssh_server, paramiko_kwargs):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ssh_server, **paramiko_kwargs)
        self.ftp = ssh.open_sftp()

    def get_identifier_chunk(self, path):
        """Get an identifier chunk from a path to an mmdd directory.

        :param str path: to a directory on the remote server. 

        :returns an identifier string, e.g. 'mvol-0004-1930-0103'.
        """

        # get everything after 'IIIF_Files' in the path.
        shortened_path_chunks = re.sub('^.*IIIF_Files/', '', path).split('/')

        if shortened_path_chunks[0] in ('ewm', 'gms', 'speculum'):
            return shortened_path_chunks.pop()
        if shortened_path_chunks[0] in ('mvol',):
            return '-'.join(shortened_path_chunks[:4])
        else:
            raise NotImplementedError

    def get_identifier(self, path):
        identifier_chunk = self.get_identifier_chunk(path)
        if self.is_identifier(identifier_chunk):
            return identifier_chunk
        else:
            raise ValueError

    def get_path(self, identifier_chunk):
        """Return the path to a given identifier chunk on owncloud's disk space.
        N.B., you should use these paths for read-only access.

        :param str identifier chunk: e.g., 'mvol-0001', 'mvol-0001-0002-0003'

        :returns a string, the path to an identifier chunk on disk. 
        """

	# for ewm, gms, and speculum, sections of the identifier are repeated
	# in subfolders, e.g. ewm/ewm-0001
        if self.get_project(identifier_chunk) in ('ewm', 'gms', 'speculum'):
            subfolders = []
            identifier_sections = identifier_chunk.split('-')
            for i in range(0, len(identifier_sections)):
                subfolders.append('-'.join(identifier_sections[:i+1]))
            return '/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/{}'.format(
                '/'.join(subfolders)
            )
	# for mvol, sections of the identifier are not repeated in subfolders,
	# e.g. mvol/0001/0002/0003.
        if self.get_project(identifier_chunk) in ('mvol',):
            return '/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/{}'.format(identifier_chunk.replace('-', '/'))
        else:
            raise NotImplementedError

    def get_project(self, identifier_chunk):
        """Return the first part of an identifier chunk, e.g. 'mvol'.

        :param str identifier_chunk: e.g. 'mvol-0001'

        :rtype str
        :returns the first part of the identifier chunk.
        """

        project = re.sub('-.*', '', identifier_chunk)
        if project in ('ewm', 'gms', 'mvol', 'speculum'):
            return project
        else:
            raise NotImplementedError

    def is_identifier(self, identifier_chunk):
        """Return true if this identifier chunk is a complete identifier. 

        :param str identifier_chunk: e.g., 'mvol-0001', 'mvol-0001-0002-0003'

        :returns True or False
        """

        if self.get_project(identifier_chunk) == 'ewm':
            return re.match('^ewm-\d{4}$', identifier_chunk)
        elif self.get_project(identifier_chunk) == 'gms':
            return re.match('^gms-\d{4}$', identifier_chunk)
        elif self.get_project(identifier_chunk) == 'mvol':
            return re.match('^mvol-\d{4}-\d{4}-\d{4}$', identifier_chunk)
        elif self.get_project(identifier_chunk) == 'speculum':
            return re.match('^speculum-\d{4}', identifier_chunk)
        else:
            raise NotImplementedError

    def is_identifier_chunk(self, identifier_chunk):
        """Return true if this is a valid identifier chunk.

	:param str identifier_chunk: check to see if this identifier chunk is
        valid.

        :returns True or False
        """

        if self.get_project(identifier_chunk) == 'ewm':
            r = '^ewm(-\d{4})?$'
        elif self.get_project(identifier_chunk) == 'gms':
            r = '^gms(-\d{4})?$'
        elif self.get_project(identifier_chunk) == 'mvol':
            r = '^mvol(-\d{4}(-\d{4}(-\d{4})?)?)?$'
        elif self.get_project(identifier_chunk) == 'speculum':
            r = '^speculum(-\d{4})?'
        else:
            raise NotImplementedError

        return bool(re.match(r, identifier_chunk))

    def recursive_ls(self, identifier_chunk):
        """Get a list of identifiers in on disk. 

        :param str identifier chunk: e.g., 'mvol-0001', 'mvol-0001-0002-0003'

        :returns a list of identifiers, e.g. 'mvol-0001-0002-0003'
        """

        if self.is_identifier(identifier_chunk):
            return [identifier_chunk]
        else:
            identifiers = []
            path = self.get_path(identifier_chunk)
            try:
                for entry in self.ftp.listdir(path):
                    entry_identifier_chunk = self.get_identifier_chunk(
                        '{}/{}'.format(path, entry)
                    )
                    if self.is_identifier_chunk(entry_identifier_chunk):
                        identifiers = identifiers + \
                            self.recursive_ls(entry_identifier_chunk)
            except FileNotFoundError:
                return []
            return identifiers

    def get_newest_modification_time_from_directory(self, directory):
        """ Helper function for get_newest_modification_time. Recursively searches
        subdirectories for the newest modification time. 

        :param ftp: paramiko ftp instance
        :param str directory: path to an identifier's files on disk, on either
        owncloud or one of the XTF servers.

        :returns the newest unix timestamp present in that directory.
        """

        mtimes = []
        for entry in ftp.listdir_attr(directory):
            if stat.S_ISDIR(entry.st_mode):
                mtime = get_newest_modification_time_from_directory(
                    ftp, '{}/{}'.format(directory, entry.filename))
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

    @staticmethod
    def _validate_file_notempty(f):
        """Make sure that a given file is not empty.

        :param f: a file-like object.
        """
        errors = []

        f.seek(0, os.SEEK_END)
        size = f.tell()

        if not size:
            try:
                errors.append('{} is an empty file.\n'.format(f.name))
            except AttributeError:
                errors.append('empty file.\n')
        return errors


class OwnCloudSSH(SSH):
    def get_csv_data(self, identifier_chunk):
        """Get CSV data for a specific identifier chunk.

        :param str identifier_year: e.g. 'mvol-0004-1951'

        :returns a dict of data about these identifiers.
        """
        path = self.get_path(identifier_chunk)
        csv_data = {}
        for entry in self.ftp.listdir(path):
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

    def validate_directory(self, identifier, folder_name):
        """A helper function to validate ALTO, JPEG, and TIFF folders inside mmdd
        folders.

        :param str identifier: e.g. 'mvol-0001-0002-0003'
        :param str folder_name: the name of the folder: ALTO|JPEG|TIFF

        :returns a list of error messages, or an empty list.
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
        self.ftp.stat(mmdd_path + '/' + folder_name)

        filename_re = '^%s-%s-%s-%s_\d{4}\.%s$' % (
            mmdd_path.split('/')[-4],
            mmdd_path.split('/')[-3],
            mmdd_path.split('/')[-2],
            mmdd_path.split('/')[-1],
            extensions[folder_name]
        )

        entries = []
        for entry in self.ftp.listdir('{}/{}'.format(mmdd_path, folder_name)):
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

        :param str identifier: 'mvol-0001-0002-0003'

        :returns a list of error messages, or an empty list.
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

        :param str identifier: e.g. 'mvol-0001-0002-0003'

        :returns a list of error messages, or an empty list.
        """

        assert self.get_project(identifier) == 'mvol'

        try:
            return self.validate_directory(identifier, 'JPEG')
        except IOError:
            return ['{}/JPEG missing\n'.format(self.get_path(identifier))]

    def validate_tiff_directory(self, identifier):
        """Validate that an TIFF folder exists. Make sure it contains appropriate
        files.

        :param str identifier: e.g. 'mvol-0001-0002-0003'

        :returns a list of error messages, or an empty list.
        """

        assert self.get_project(identifier) == 'mvol'
        try:
            return self.validate_directory(identifier, 'TIFF')
        except IOError:
            return ['{}/TIFF missing\n'.format(self.get_path(identifier))]

    def validate_dc_xml(self, identifier, f=None):
        """Make sure that a given dc.xml file is well-formed and valid, and that the
        date element is arranged as yyyy-mm-dd.

        :param str identifier: e.g. 'mvol-0001-0002-0003'
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

        :param str identifier: e.g. 'mvol-0001-0002-0003'
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
        return errors

    def validate_struct_txt(self, identifier, f=None):
        """Make sure that a given struct.txt is valid. It should be tab-delimited
        data, with a header row. Each record should contains a field for object,
        page and milestone.

        :param str identifier: e.g. 'mvol-0001-0002-0003'
        :param f: a file-like object, for testing. 
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

        :param str identifier: e.g. 'mvol-0001-0002-0003'
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

        :param str identifier: e.g. 'mvol-0001-0002-0003'
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

        :param str identifier: e.g. 'mvol-0001-0002-0003'
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

        :param str identifier: e.g. 'mvol-0001-0002-0003'
        """

        assert self.get_project(identifier) == 'mvol'

        errors = []
        errors = errors + self.validate_alto_or_pos_directory(identifier)
        errors = errors + self.validate_jpeg_directory(identifier)
        errors = errors + self.validate_tiff_directory(identifier)
        errors = errors + self.validate_mets_xml(identifier)
        errors = errors + self.validate_pdf(identifier)
        errors = errors + self.validate_struct_txt(identifier)
        errors = errors + self.validate_txt(identifier)
        errors = errors + self.validate_dc_xml(identifier)
        if not errors:
            errors = self.finalcheck(identifier)

        return errors


class XTFSSH(SSH):
    def __init__(self, production):
        super().__init__()
        self.production = production

    @staticmethod
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

        :param str identifier: e.g. 'mvol-0001-0002-0003'

        :rtype str
        :returns the path to this file on owncloud.
        """

        return '/IIIF_Files/{}'.format(identifier.replace('-', '/'))

    @staticmethod
    def get_identifier(self, path):
        """Return an identifier for a given owncloud path. 

        :param str identifier: e.g. 'IIIF_Files/mvol/0001/0002/0003/ALTO/0001.xml'

        :rtype str
        :returns an identifier, e.g. 'mvol-0001-0002-0003'
        """

        m = re.search(path, 'IIIF_Files/(mvol)/(\d{4})/(\d{4})/(\d{4})/')
        return '{}-{}-{}-{}'.format(m.group(1), m.group(2), m.group(3), m.group(4))

    def regularize_mvol_file(self, identifier, extension):
        """Regularize METS, PDF, .txt or .struct.txt filenames. 

        :param str identifier: e.g. 'mvol-0001-0002-0003'
        :param str extension: e.g. '.mets.xml'
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

        :param str directory: e.g. 'IIIF_Files/mvol/0001/0002/0003/ALTO/'
        :param pattern_fun: a pattern function. 
        """

        assert identifier.split('-')[0] == 'mvol'

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

        :param str identifier: e.g., 'mvol-0001-0002-0003'
        """

        assert identifier.split('-')[0] == 'mvol'

        remote_path = '{}/{}.dc.xml'.format(
            OwnCloudWebDAV.get_path(identifier), identifier)
        try:
            self.oc.file_info(remote_path)
            sys.stdout.write(
                'A .dc.xml file already exists in that location.\n')
            sys.exit()
        except owncloud.HTTPResponseError:
            pass

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

        :param str identifier: e.g. 'mvol-0001-0002-0003'

        :returns a string, the title for an identifier chunk like 'mvol-0004'.
        """

        identifier_chunk = '-'.join(identifier.split('-')[:2])
        titles = {
            'mvol-0004': 'Daily Maroon',
        }
        return titles[identifier_chunk]

    @staticmethod
    def get_dc_description(identifier):
        """Return the description for a given identifier.

        :param str identifier: e.g. 'mvol-0001-0002-0003'

        :returns a string, the description for an identifier chunk like 'mvol-0004'.
        """

        identifier_chunk = '-'.join(identifier.split('-')[:2])
        descriptions = {
            'mvol-0004': 'A newspaper produced by students of the University of Chicago. Published 1902-1942 and continued by the Chicago Maroon.'
        }
        return descriptions[identifier_chunk]

    @staticmethod
    def get_dc_date(identifier):
        """Return the date for a given identifier.

        :param str identifier: e.g. 'mvol-0004-1938-0103'

        :returns a string, e.g. '1938-01-03'
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

        :param int index: the index of this file, e.g. 1, 2, etc. 
        :param str path: e.g., 'IIIF_Files/mvol/0001/0002/0003/ALTO/'

        :returns a correctly named file, e.g. 'mvol-0001-0002-0003_0001.xml'
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
            extensions[matches.group(5)]
        )
