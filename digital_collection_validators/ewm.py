#!/usr/bin/env python3

"""Usage:
   chopin ls <identifier-chunk> ...
   chopin validate (--list-valid | --show-errors) <identifier-chunk> ...
"""

import os
import sys
from classes import *
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)

    ewm_owncloud_ssh = EwmOwnCloudSSH()
    ewm_owncloud_ssh.connect(os.environ['OWNCLOUD_SSH_SERVER'], {})

    identifiers = []
    for i in range(0,len(arguments['<identifier-chunk>'])):
        identifiers.insert(i,(ewm_owncloud_ssh.list_directory(arguments['<identifier-chunk>'][i])))

    if arguments['ls']:
        for identifier in identifiers:
            for i in identifier:
                sys.stdout.write(i + '\n')


    elif arguments['validate']:
        for identifier in identifiers:
            errors = apf_owncloud_ssh.validate(identifier)
            if arguments['--show-errors']:
                for error in errors:
                    sys.stdout.write(error)
            elif arguments['--list-valid']:
                if not errors:
                    sys.stdout.write('{}\n'.format(identifier))