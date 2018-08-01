import argparse
import owncloud
import os
import getpass
import sys
import re

def get_mvol_mmdd_directories(oc, file_info):
  '''Get a list of mvol mmdd directories, from anywhere in the
     directory hierarchy on owncloud.
  '''
  raise NotImplementedError
    
def get_sentinel_files(oc, file_info):
  '''Get the sentinel files in a given mmdd directory.

     Arguments:
     oc, an owncloud object. 
     file_info, an owncloud.FileInfo object describing an mmdd directory.

     Returns:
     a list of owncloud.FileInfo objects in this directory. 

  sentinels = []
  for entry in oc.list(file_info):
    if entry.get_name() in ('ready', 'queue', 'valid', 'invalid'):
      sentinels.append(oc.file_info(entry.path))
  return sentinels
  '''

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

  sentinels = get_sentinel_files(oc, file_info)
  if mode == "addready" and len(sentinels) == 0:
    oc.put_file(f_in, "ready")
  elif mode == "fix" and len(sentinels) > 1:
    for s in sentinels:
      oc.delete(s)
  elif mode == "deleteall":
    for s in sentinels:
      oc.delete(s)
  '''

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
 
  for file_info in get_mvol_mmdd_directories(args.directory):
    runutil(oc, file_info, args.mode)
