import re
import json
from password import ocpassword
import owncloud
import os
import requests

def filterbottom(oc, p):
    print(p)
    if re.match('mvol/\d{4}/\d{4}/\d{4}/?$', p):
        return 'IIIF_Files/' + p

def runutil(oc, file_info):
    for entry in oc.list(file_info.get_path()):
        if entry.get_name() == 'ready':
            oc.delete(entry)
            os.utime("queue")
            oc.put_file(file_info, "queue")
            break

username = "ldr_oc_admin"
password = ocpassword
oc = owncloud.Client('https://s3.lib.uchicago.edu/owncloud')
oc.login(username, password)

r = requests.get('https://www2.lib.uchicago.edu/keith/tmp/cai.json')
r = r.json()
allreadies = r['ready']

allreadiesfiltered = []
for rt in allreadies:
    allreadiesfiltered = allreadiesfiltered + [filterbottom(oc, rt)]

for rt in allreadiesfiltered:
    runutil(oc, oc.file_info(rt))