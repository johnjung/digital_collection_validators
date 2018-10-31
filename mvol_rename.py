"""Usage:
    mvol_rename.py <owncloud-path>
"""

from docopt import docopt
import getpass
import os
import owncloud
import sys

if __name__ == '__main__':
  arguments = docopt(__doc__)
  directory = arguments['<owncloud-path>']
  
  try:
    #oc = owncloud.Client(os.environ['OWNCLOUD_SERVER'])
    oc = owncloud.Client('https://s3.lib.uchicago.edu/owncloud')
  except KeyError:
    sys.stderr.write("OWNCLOUD_SERVER environmental variable not set.\n")
    sys.exit()

  username = input('WebDAV username: ')
  password = getpass.getpass('WebDAV password: ')

  oc.login(username, password)

  for entry in oc.list(directory):
    old_name = entry.get_path() + '/' + entry.get_name()
    new_name = entry.get_path() + '/' + entry.get_name().replace('mvol-0004-1974', 'mvol-0004-1947')
    if old_name != new_name:
      oc.move(old_name, new_name)

