"""Usage:
    put_mvol_dc_xml.py [--force] <owncloud-username> <identifier>
"""

from docopt import docopt
import getpass
import owncloud
import re
import sys


def get_title(identifier):
    identifier_chunk = '-'.join(identifier.split('-')[:2])
    titles = {
        'mvol-0004': 'Daily Maroon',
    }
    return titles[identifier_chunk]


def get_description(identifier):
    identifier_chunk = '-'.join(identifier.split('-')[:2])
    descriptions = {
        'mvol-0004': 'A newspaper produced by students of the University of Chicago. Published 1902-1942 and continued by the Chicago Maroon.'
    }
    return descriptions[identifier_chunk]


def get_date(identifier):
    if re.search('^mvol-0004-\d{4}-\d{4}$', identifier):
        return '{}-{}-{}'.format(
            identifier.split('-')[-2],
            identifier.split('-')[-1][:2],
            identifier.split('-')[-1][2:]
        )
    else:
        raise ValueError


def get_path(identifier):
    '''return the path to an mmdd directory, given an identifier.'''
    if re.search('^mvol-0004-\d{4}-\d{4}$', identifier):
        return 'IIIF_Files/{}'.format('/'.join(identifier.split('-')))
    else: 
        raise ValueError


if __name__ == '__main__':
    arguments = docopt(__doc__)
    identifier = arguments['<identifier>']
    username = arguments['<owncloud-username>']
    force = arguments['--force']

    password = getpass.getpass('WebDAV password: ')

    oc = owncloud.Client('https://s3.lib.uchicago.edu/owncloud')

    try:
        oc.login(username, password)
    except owncloud.HTTPResponseError:
        sys.stderr.write('incorrect WebDAV password.\n')
        sys.exit()

    remote_path = 'IIIF_Files/{}/{}.dc.xml'.format(identifier.replace('-', '/'), identifier)

    if force:
        print(oc.file_info(remote_path))
        oc.delete(remote_path)

    try:
        oc.file_info(remote_path)
        sys.stdout.write('A .dc.xml file already exists in that location.\n')
        sys.exit()
    except owncloud.HTTPResponseError:
        pass

    xml_data = "<?xml version='1.0' encoding='utf8'?><metadata><title>{}</title><date>{}</date><description>{}</description><identifier>{}</identifier></metadata>".format(
        get_title(identifier),
        get_date(identifier),
        get_description(identifier),
        identifier
    )

    oc.put_file_contents(remote_path, xml_data)
