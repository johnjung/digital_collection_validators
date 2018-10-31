"""Usage:
    put_mvol_data_xtf.py <owncloud-ssh-username> <xtf-ssh-username> <identifier> <min-year> <max-year> <development_or_production>
"""

from docopt import docopt
from PIL import Image
import getpass
import io
import paramiko
import re
import requests
import statistics
import sys


if __name__ == '__main__':
    arguments = docopt(__doc__)
    owncloud_username = arguments['<owncloud-ssh-username>']
    xtf_username = arguments['<xtf-ssh-username>']
    identifier = arguments['<identifier>']
    min_year = arguments['<min-year>']
    max_year = arguments['<max-year>']
    development_or_production = arguments['<development_or_production>']

    owncloud_password = getpass.getpass('Owncloud password: ')
    xtf_password = getpass.getpass('XTF password: ')

    owncloud_path = '/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files'

    if development_or_production == 'development':
        xtf_server = 'campub-xtf.lib.uchicago.edu'
        xtf_path = '/usr/local/apache-tomcat-6.0/webapps/xtf/data/bookreader'
    elif development_or_production == 'production':
        xtf_server = 'xtf.lib.uchicago.edu'
        xtf_path = '/usr/local/apache-tomcat-6.0/webapps/campub/data/bookreader'
    else:
        sys.stdout.write('unknown server, must be development or production.\n')
        sys.exit()

    owncloud_ssh = paramiko.SSHClient()
    owncloud_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    owncloud_ssh.connect('s3.lib.uchicago.edu', username=owncloud_username, password=owncloud_password)
    owncloud_ftp = owncloud_ssh.open_sftp()

    xtf_ssh = paramiko.SSHClient()
    xtf_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    xtf_ssh.connect(xtf_server, username=xtf_username, password=xtf_password)
    xtf_ftp = xtf_ssh.open_sftp()

    # assume that the directory has been validated. 

    try:
        xtf_ftp.stat(xtf_path + '/' + identifier)
        sys.stdout.write('This directory exists on the XTF server.\n')
        sys.exit()
    except FileNotFoundError:
        pass

    xtf_ftp.mkdir('{}/{}'.format(xtf_path, identifier), mode=0o755)

    img_dir = owncloud_path + '/' + '/'.join(identifier.split('-')) + '/' + 'JPEG'
    imgs= []
    for img in owncloud_ftp.listdir(img_dir):
        imgs.append(img_dir + '/' + img)
    imgs.sort()

    if identifier.startswith('mvol-0004'):
        size = (6800, 6800)
    else:
        size = (1024, 1024)

    sizes = []
    i = 1
    for img in imgs:
        in_memory_in = io.BytesIO()
        in_memory_out = io.BytesIO()
        owncloud_ftp.getfo(img, in_memory_in)
        im = Image.open(in_memory_in)
        im.thumbnail(size)
        sizes.append(im.size)
        im.save(in_memory_out, format='JPEG')
        in_memory_out.seek(0)
        xtf_ftp.putfo(in_memory_out, '{}/{}/{}.jpg'.format(xtf_path, identifier, str(i).zfill(8)))

        if i == 1:
            in_memory_out = io.BytesIO()
            im = Image.open(in_memory_in)
            im.thumbnail((100, 100))
            im.save(in_memory_out, format='JPEG')
            in_memory_out.seek(0)
            xtf_ftp.putfo(in_memory_out, '{}/{}/{}.jpg'.format(xtf_path, identifier, identifier))
        i = i + 1

    width = int(statistics.median([s[0] for s in sizes]))
    height = int(statistics.median([s[1] for s in sizes]))

    url = 'https://digcollretriever.lib.uchicago.edu/projects/{}/ocr?jpg_width={}&jpg_height={}&min_year={}&max_year={}'.format(
        identifier,
        width,
        height,
        min_year,
        max_year
    )
    in_memory_ocr = io.StringIO()
    ocr_text = requests.get(url).text
    in_memory_ocr.write(ocr_text)
    in_memory_ocr.seek(0)
    try:
        xtf_ftp.putfo(in_memory_ocr, '{}/{}/{}.xml'.format(xtf_path, identifier, identifier))
    except OSError:
        pass

