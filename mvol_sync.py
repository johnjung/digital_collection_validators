import argparse
import getpass
import os
import owncloud
import paramiko
import sys

def get_last_mod_date_from_owncloud(oc, directory):
  '''
     Arguments:
     directory, e.g. "IIIF_Files/mvol/0004/0030/0103"
 
     Returns:
     datetime object.
  '''
 
  raise NotImplementedError

def get_last_mod_date_from_xtf(directory, server):
  '''
     Arguments:
     directory, e.g. "/usr/local/apache-tomcat-6.0/webapps/campub/data/bookreader/mvol-0004-0030-0103"
     server, e.g. development, production
 
     Returns:
     datetime object.
  '''

  hostnames = {
    'development': 'campub-xtf.lib.uchicago.edu',
    'production': 'xtf.lib.uchicago.edu'
  }

  password = getpass.getpass('SSH password: ')

  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.WarningPolicy)
  ssh.load_system_host_keys()
  ssh.connect(hostnames[server], username='xtf', password=password)

  #raise NotImplementedError

def identifier_to_path(identifier, server):
  '''
     Arguments:
     identifier, e.g. "mvol", "mvol-0004", "mvol-0004-0030-0103"
     server, e.g. owncloud, development, production. 
 
     Returns:
     path, e.g. "/usr/local/apache-tomcat-6.0/webapps/campub/data/bookreader/mvol-0004-0030-0103"
  '''

  if server == 'owncloud':
    return 'IIIF_Files/{}'.format(identifier.replace('-', '/'))
  elif server == 'development':
    return 'xtf@campub-xtf.lib.uchicago.edu:/usr/local/apache-tomcat-6.0/webapps/xtf/data/bookreader/{}'.format(identifier)
  elif server == 'production':
    return 'xtf@xtf.lib.uchicago.edu:/usr/local/apache-tomcat-6.0/webapps/campub/data/bookreader/{}'.format(identifier)
  else:
    raise NotImplementedError
       
if __name__ == '__main__':
  """ Check to see which directories are out of sync between owncloud,
      development and production. 

      List all of the owncloud directories under "mvol". Show if they are
      valid, and if files are present and in sync in dev and production.
      python mvol_sync.py --list mvol

      List all of the owncloud directories under "mvol-0004". Show if they are
      valid, and if files are present and in sync in dev and production.
      python mvol_sync.py --list mvol-0004

      List all of the owncloud directories under "mvol-0004-0030". Show if they
      are valid, and if files are present and in sync in dev and production.
      python mvol_sync.py --list mvol-0004-0030

      Copy files from owncloud to the development server:
      python mvol_sync.py --copy-to-dev mvol-0004-0030-0103

      Copy files from owncloud to the production server:
      python mvol_sync.py --copy-to-dev mvol-0004-0030-0103
  """

  parser = argparse.ArgumentParser()
  parser.add_argument("identifier", help="e.g. mvol-0004-0030-0103")

  args = parser.parse_args()

  try:
    oc = owncloud.Client(os.environ['OWNCLOUD_SERVER'])
  except KeyError:
    sys.stderr.write("OWNCLOUD_SERVER environmental variable not set.\n")
    sys.exit()

  username = input('WebDAV username: ')
  password = getpass.getpass('WebDAV password: ')

  print(get_last_mod_date_from_xtf(identifier_to_path(args.identifier, 'development'), 'development'))
