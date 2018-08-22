import owncloud
import os
import getpass
import sys
import re
import tempfile
from ..data.password import ocpassword

def get_mvol_mmdd_directories(oc, p):
  '''Get a list of mvol mmdd directories from a given path. 
     Arguments:
     oc, an owncloud object.
     p, the directory path as a string, e.g. "IIIF_Files/mvol/0004/1930"
     Returns: 
     a list of strings, paths to mmdd directories. 
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
  '''
  sentinels = get_sentinel_files(oc, file_info)
  if mode == "addready" and len(sentinels) == 0:
    os.utime("workflowautomator/utilities/ready")
    oc.put_file(file_info, "workflowautomator/utilities/ready")
  elif mode == "fix" and len(sentinels) > 1:
    for s in sentinels:
      if s.get_name() in ('ready', 'queue', 'valid', 'invalid'):
        oc.delete(s)
  elif mode == "deleteall":
    for s in sentinels:
      if s.get_name() in ('ready', 'queue', 'valid', 'invalid'):
        oc.delete(s)
  
def plant(directory, mode):
  username = "ldr_oc_admin"
  password = ocpassword
  oc = owncloud.Client('https://s3.lib.uchicago.edu/owncloud')
  oc.login(username, password)

  for p in get_mvol_mmdd_directories(oc, ("/IIIF_Files/" + directory).replace('-', '/')):
    runutil(oc, oc.file_info(p), mode)