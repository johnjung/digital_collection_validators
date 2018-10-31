"""Usage:
   mvol_ls.py <identifier-chunk>
"""

from docopt import docopt
import getpass
import paramiko
import re
import sys


def is_identifier(identifier_chunk):
  """Return true if this identifier chunk is a complete identifier. 

     Arguments:
     identifier -- e.g., mvol, mvol-0001, mvol-0001-0002, mvol-0001-0002-0003

     Returns:
     True or False
  """
  
  return re.match('^mvol-\d{4}-\d{4}-\d{4}$', identifier_chunk)


def get_path(identifier_chunk):
  return '/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/{}'.format(identifier_chunk.replace('-', '/'))


def recursive_ls(ftp, identifier_chunk):
  """Get a list of identifiers in on disk. 
  """
  # really should check to be sure the identifier actually exists on disk..
  if is_identifier(identifier_chunk):
    return [identifier_chunk]
  else:
    identifiers = []
    for entry in ftp.listdir(get_path(identifier_chunk)):
      if re.match('^\d{4}$', entry):
        identifiers = identifiers + recursive_ls(ftp, '{}-{}'.format(identifier_chunk, entry))
    return identifiers
  

if __name__ == '__main__':
  """ List mvols that match certain patterns. 
      mvol 
      mvol-0001
      mvol-0001-0001
      mvol-0001-0001-0001
  """
  arguments = docopt(__doc__)
  identifier_chunk = arguments['<identifier-chunk>']

  username = ''
  password = getpass.getpass('SSH password or passphrase: ')

  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect('s3.lib.uchicago.edu', username=username, password=password)
  ftp = ssh.open_sftp()

  identifiers = recursive_ls(ftp, identifier_chunk)
  identifiers.sort()
  for identifier in identifiers:
    print(identifier)

