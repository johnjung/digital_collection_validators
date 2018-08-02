import argparse
import owncloud
import os
import getpass
import sys
import re
import tempfile

def get_mvol_mmdd_directories(oc, p):
  '''be sure the current file_info is a directory.
     get full path- if the end of the full path matches mvol/\d{4}/\d{4}/\d{4}$, this is an mvol directory, return it. 
     else, this is not yet an mmdd. for each entry in this directory, return get_mvol_mmdd_directories(oc, entry)

     oc- owncloud object.
     p- a string, path to a directory. 
 
     returns a list of strings, paths to mmdd directories. 
  '''

  if re.match('^/?IIIF_Files/mvol/\d{4}/\d{4}/\d{4}/?$', p):
    return [p]
  elif re.match('^/?IIIF_Files/mvol(/\d{4}){0,3}/?$', p):
    directories = []
    for e in oc.list(p):
      if e.is_dir():
        directories = directories + get_mvol_mmdd_directories(oc, e.path)
    return directories
  else:
    return []

def get_sentinel_files(oc, file_info):
  '''Get the sentinel files in a given mmdd directory.

     Arguments:
     oc, an owncloud object. 
     file_info, an owncloud.FileInfo object describing an mmdd directory.

     Returns:
     a list of owncloud.FileInfo objects in this directory. 
  '''
  sentinels = []
  for entry in oc.list(file_info.get_path()):
    if entry.get_name() in ('ready', 'queue', 'valid', 'invalid'):
      sentinels.append(oc.file_info(entry.path))
  return sentinels

def runutil(oc, file_info, mode):
  '''
     Modify the sentinel files in a given mmdd directory.
 
     Arguments:
     oc, an owncloud object. 
     file_info, an owncloud.FileInfo object describing an mmdd directory.
     mode, "addready"|"fix"|"deleteall".

     Side effect:
     manages sentinel files.
  
     TODO: 
     create files in a temporary directory.
  '''
  sentinels = get_sentinel_files(oc, file_info)
  if mode == "addready" and len(sentinels) == 0:
    oc.put_file(file_info, "ready")
  elif mode == "fix" and len(sentinels) > 1:
    for s in sentinels:
      if s.get_name() in ('ready', 'queue', 'valid', 'invalid'):
        oc.delete(s)
  elif mode == "deleteall":
    for s in sentinels:
      if s.get_name() in ('ready', 'queue', 'valid', 'invalid'):
        oc.delete(s)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("username", help="WebDAV username.")
  parser.add_argument("directory", help="e.g. IIIF_Files/mvol/0004/1930/0103")
  parser.add_argument("mode", help='''addready to add ready to all empty folders,
                      fix to delete sentinel files from any folder with more than one,
                      deleteall to delete all sentinel files''')
  args = parser.parse_args()
 
  # TODO can we move this into add_argument above? 
  if not args.mode in ('addready', 'fix', 'deleteall'):
    sys.stderr.write("Mode is invalid, use addready, fix, or deleteall.")
    sys.exit()
  
  try:
    oc = owncloud.Client(os.environ['OWNCLOUD_SERVER'])
  except KeyError:
    sys.stderr.write("OWNCLOUD_SERVER environmental variable not set.\n")
    sys.exit()
  
  password = getpass.getpass('WebDAV password: ')
  
  try:
    oc.login(args.username, password)
  except owncloud.HTTPResponseError:
    sys.stderr.write('incorrect WebDAV password.\n')
    sys.exit()
  
  if(args.mode == "addready"):
    temptuple = tempfile.mkstemp()
    fd = os.fdopen(temptuple[0])
    fd.close()
    os.rename(temptuple[1], "ready")
  
  for p in get_mvol_mmdd_directories(oc, args.directory):
    runutil(oc, oc.file_info(p), args.mode)

  if(args.mode == "addready"):
    os.remove("ready")