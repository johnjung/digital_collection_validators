import owncloud
import os
import getpass
import sys
import re
import tempfile
import json
import random

def statusrecurse(start):
  #print("pass")
  if not 'children' in start:
    return (start['owncloud'][0], start['development'][0], start['production'][0])
  else:
    valids = []
    devs = []
    pros = []
    mostrecent = 0
    mostdev = 0
    mostpro = 0
    for child in start['children'].items():
      gift = statusrecurse(child[1])
      valids.append(gift[0])
      devs.append(gift[1])
      pros.append(gift[2])
      if child[1]['owncloud'][1] > mostrecent:
        mostrecent = child[1]['owncloud'][1]
      if child[1]['development'][1] > mostrecent:
        mostdev = child[1]['development'][1]
      if child[1]['production'][1] > mostrecent:
        mostpro = child[1]['production'][1]
    first = "valid"
    first = "valid"
    second = "in-sync"
    third = "in-sync"
    if "invalid" in valids:
      first = "invalid"
    if "out-of-sync" in devs:
      second = "out-of-sync"
    else:
      start['development'][1] = mostdev
    if "out-of-sync" in pros:
      second = "out-of-sync"
    else:
      start['production'][1] = mostpro
    start['owncloud'][0] = first
    start['owncloud'][1] = mostrecent
    start['development'][0] = second
    start['production'][0] = third
    return(first, second, third)

def chxistnrecent(currtime, comparetime):
  # checks if two times exist and compares them
  if comparetime:
    if comparetime < currtime:
      return "out-of-sync"
    else:
      return "in-sync"
  else:
    return None

def buildwithoutchild(start, name):
  #the lines that are commented out determine whether
  # valids and in-syncs are guaranteed or not

  name = name.replace("/", "-")
  #validornot = random.randint(0,1) 
  validornot = 1
  if validornot:
    first = "valid"
  else:
    first = "invalid"

  firstdate = random.randint(0, 1227148486)
  #seconddate = random.randint(0, 1227148486)
  seconddate = random.randint(firstdate + 1, 1227148486)
  thirddate = random.randint(seconddate, 1227148486)
  if not validornot:
    second = "none"
    third = "none"
  else:
    second = chxistnrecent(firstdate, seconddate)
    third = chxistnrecent(firstdate, thirddate)


  start[name] = { "owncloud" : [first, firstdate],
                  "development" : [second, seconddate],
                  "production" : [third, thirddate]}

def buildwithchild(start, name):
  name = name.replace("/", "-")
  start[name] = { "owncloud" : ["none", None],
                  "development" : ["none", None],
                  "production" : ["none", None],
                  "children" : {}}

def build(startfolder, namesofar, ocfolder, layer):
  #commented out lines determine whether just mvol/0004 is read, or everything
  if layer != 2:
    for f in oc.list(ocfolder):
      tname = f.get_name()
      tname = namesofar + "/" + tname
      #print(tname)
      #if re.match('^/?IIIF_Files/mvol/0004(/\d{4}){0,2}/?$', "IIIF_Files/" + tname):
      if re.match('^/?IIIF_Files/mvol(/\d{4}){0,3}/?$', "IIIF_Files/" + tname):
        #print("made it")
        buildwithchild(startfolder['children'], tname)
        build(startfolder['children'][tname.replace("/", "-")], tname, "IIIF_Files/" + tname, layer + 1)
  else:
    for f in oc.list(ocfolder):
      tname = f.get_name()
      tname = namesofar + "/" + tname
      #print(tname)
      #if re.match('^/?IIIF_Files/mvol/0004(/\d{4}){0,2}/?$', "IIIF_Files/" + tname):
      if re.match('^/?IIIF_Files/mvol(/\d{4}){0,3}/?$', "IIIF_Files/" + tname):
        buildwithoutchild(startfolder['children'], tname)

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

if __name__ == '__main__':
  
  try:
    oc = owncloud.Client(os.environ['OWNCLOUD_SERVER'])
  except KeyError:
    sys.stderr.write("OWNCLOUD_SERVER environmental variable not set.\n")
    sys.exit()
  
  username = "ldr_oc_admin"
  password = ""
  
  try:
    oc.login(username, password)
  except owncloud.HTTPResponseError:
    sys.stderr.write('incorrect WebDAV password.\n')
    sys.exit()  
  mainfile = {}
  buildwithchild(mainfile, "mvol")
  build(mainfile['mvol'], "mvol","IIIF_Files/mvol", 0)
  statusrecurse(mainfile['mvol'])
  with open('snar.json', 'w') as fp:
    json.dump(mainfile, fp)
  print("done")