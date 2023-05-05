#!/usr/bin/env python3

"""Usage:
   make_mvol_jpegs --local-root=<local-root> <identifier-chunk>
"""

import os, pathlib, re, sys
from docopt import docopt
from PIL import Image

def identifier_chunk_to_path(root, identifier_chunk):
    """Get a path on disk from a root and identifier chunk."""
    return root + os.path.sep + os.path.sep.join(identifier_chunk.split('-')) 

def get_identifiers_under_root(root):
    """Get identifiers under some root in the filesystem."""
    identifiers = set()
    for root, dirs, files in os.walk(root):
        for f in files:
            if re.match('^mvol-[0-9]{4}-[0-9]{4}-[0-9]{4}\.dc\.xml$', f):
                identifiers.add(f.replace('.dc.xml', ''))
    return sorted(list(identifiers))

if __name__ == '__main__':
    arguments = docopt(__doc__)

    for identifier in get_identifiers_under_root(
        arguments['--local-root']
    ):
        jpg_dir = None
        tif_dir = None
        mvol_dir = identifier_chunk_to_path(arguments['--local-root'], identifier)
        if os.path.exists('{}{}TIFF'.format(mvol_dir, os.path.sep)):
            jpg_dir = '{}{}JPEG'.format(mvol_dir, os.path.sep)
            tif_dir = '{}{}TIFF'.format(mvol_dir, os.path.sep)
        elif os.path.exists('{}{}tif'.format(mvol_dir, os.path.sep)):
            jpg_dir = '{}{}jpg'.format(mvol_dir, os.path.sep)
            tif_dir = '{}{}tif'.format(mvol_dir, os.path.sep)
        else: 
            raise NotImplementedError

        if tif_dir == None:
            continue

        assert(os.path.exists(mvol_dir))
        assert(os.path.exists(tif_dir))
        assert(os.path.exists(jpg_dir) == False)

        if not os.path.isdir(jpg_dir):
            print(jpg_dir)
            os.mkdir(jpg_dir)

        for tif_file in sorted(os.listdir(tif_dir)):
            if identifier.startswith('mvol-0004') or identifier.startswith('mvol-0448'):
                size = (6800, 6800)
            else:
                size = (1024, 1024)

            im = Image.open(os.path.sep.join((tif_dir, tif_file)))

            #because no jpegs were produced for this set, the
            #coordinates match the TIFFs- so there is no need to alter
            #them. JPEGs can be saved at the same size as TIFFs. 
            #im.thumbnail(size)

            stem = pathlib.Path(os.path.sep.join((tif_dir, tif_file))).stem
            jpg_file = '{}{}{}.jpg'.format(jpg_dir, os.path.sep, stem)
            im.save(jpg_file, format='JPEG')
