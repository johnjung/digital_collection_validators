"""Usage:
    put_struct_txt.py <owncloud-username> <identifier>
"""

from docopt import docopt
import getpass
import owncloud
import re
import sys


if __name__ == '__main__':
    arguments = docopt(__doc__)
    identifier = arguments['<identifier>']
    username = arguments['<owncloud-username>']

    password = getpass.getpass('WebDAV password: ')

    oc = owncloud.Client('https://s3.lib.uchicago.edu/owncloud')

    try:
        oc.login(username, password)
    except owncloud.HTTPResponseError:
        sys.stderr.write('incorrect WebDAV password.\n')
        sys.exit()

    remote_path = 'IIIF_Files/{}/{}.struct.txt'.format(identifier.replace('-', '/'), identifier)

    try:
        oc.file_info(remote_path)
        sys.stdout.write('A .struct.txt file already exists in that location.\n')
        sys.exit()
    except owncloud.owncloud.HTTPResponseError:
        pass

    jpeg_count = 0
    for entry in oc.list('IIIF_Files/{}/JPEG'.format(identifier.replace('-', '/'))):
        if entry.get_name().startswith(identifier):
            jpeg_count = jpeg_count + 1

    txt_data = 'object\tpage\tmilestone\n'
    for i in range(1, jpeg_count + 1):
        txt_data = txt_data + '{}\t{}\n'.format(str(i).zfill(8), i)
 
    oc.put_file_contents(remote_path, txt_data)
