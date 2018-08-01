import argparse
import owncloud
import os
import getpass
import sys
import re

#parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("username", help="WebDAV username.")
parser.add_argument("directory", help="e.g. IIIF_Files/mvol/0004/1930/0103")
parser.add_argument("mode", help='''addready to add ready to all empty folders,
                    fix to delete sentinel files from any folder with more than one,
                    deleteall to delete all sentinel files''')
args = parser.parse_args()

#determine mode utility runs in
addreadymode = 1
fixmode = 2
deleteallmode = 3

if args.mode == "addready":
  currmode = addreadymode
elif args.mode == "fix":
  currmode = fixmode
elif args.mode == "deleteall":
  currmode = deleteallmode
else:
  sys.stderr.write("Mode is invalid, use addready, fix, or deleteall.")

#determine level in hierarchy
targetdir = args.directory

numforevery = 0

nodownpattern = re.compile("^IIIF_Files/mvol")
onedownpattern = re.compile("^IIIF_Files/mvol/\d{4}")
twodownpattern = re.compile("^IIIF_Files/mvol/\d{4}/\d{4}")
threedownpattern = re.compile("^IIIF_Files/mvol/\d{4}/\d{4}/\d{4}")

attemptmatch = threedownpattern.fullmatch(targetdir)

if not attemptmatch:
  numforevery += 1
  attemptmatch = twodownpattern.fullmatch(targetdir)
  if not attemptmatch:
    numforevery += 1
    attemptmatch = onedownpattern.fullmatch(targetdir)
    if not attemptmatch:
      numforevery += 1
      attemptmatch = nodownpattern.fullmatch(targetdir)
      if not attemptmatch:
        sys.stderr.write("Directory is poorly formatted.")

#login
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

def runutil(f_in):
  if currmode == addreadymode:
    i = 0
    for entry in oc.list(f_in.get_path()):
      name = entry.get_name()
      if ((name == "ready") | (name == "valid") |
      (name == "invalid") | (name == "queue")):
        i += 1
    if i == 0:
      oc.put_file(f_in, "ready")
  elif currmode == fixmode:
    i = 0
    for entry in oc.list(f_in.get_path()):
      name = entry.get_name()
      if ((name == "ready") | (name == "valid") |
      (name == "invalid") | (name == "queue")):
        i += 1
    if i > 1:
      for entry in oc.list(f_in.get_path()):
        name = entry.get_name()
        if ((name == "ready") | (name == "valid") |
      (name == "invalid") | (name == "queue")):
          oc.delete(entry)
  else:
    for entry in oc.list(f_in.get_path()):
      name = entry.get_name()
      if ((name == "ready") | (name == "valid") |
      (name == "invalid") | (name == "queue")):
        oc.delete(entry)
    
f = oc.file_info(args.directory)
if numforevery == 3:
  for entry in oc.list(f.get_path()):
    for entrydown in oc.list(entry.get_path()):
      open("ready", 'a').close()
      for entrydown1 in oc.list(entrydown.get_path()):
        runutil(entrydown)
      os.remove("ready")
elif numforevery == 2:
  for entry in oc.list(f.get_path()):
    open("ready", 'a').close()
    for entrydown in oc.list(entry.get_path()):
      runutil(entrydown)
    os.remove("ready")
elif numforevery == 1:
  open("ready", 'a').close()
  for entry in oc.list(f.get_path()):
    runutil(entry)
  os.remove("ready")
else:
  open("ready", 'a').close()
  runutil(f)
  os.remove("ready")


