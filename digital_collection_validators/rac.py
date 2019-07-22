#!/usr/bin/env python3

"""Usage:
   speculum ls <identifier-chunk> ...
   speculum validate (--list-valid | --show-errors) <identifier-chunk> ...
"""

import os
import sys
from classes import *
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)

    rac_valid = RacValidator()
    rac_valid.connect(os.environ['OWNCLOUD_SSH_SERVER'], {})

    identifiers = []
    for i in range(0,len(arguments['<identifier-chunk>'])):
        identifiers.insert(i,(rac_valid.list_dir(arguments['<identifier-chunk>'][i])))

    if arguments['ls']:
        for identifier in identifiers:
            for i in identifier:
                sys.stdout.write(i + '\n')


    elif arguments['validate']:
        for identifier in identifiers:
            errors = rac_valid.validate(identifier)
            if arguments['--show-errors']:
                for error in errors:
                    sys.stdout.write(error)
            elif arguments['--list-valid']:
                if not errors:
                    sys.stdout.write('{}\n'.format(identifier))