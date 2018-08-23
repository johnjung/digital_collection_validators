import re
import json
from ..data.password import ocpassword
import sentinelutility
import oc
import os
from mvol_validator import mainvalidate

def filterbottom(oc, p):
    if re.match('mvol/\d{4}/\d{4}/\d{4}/?$', p):
        return 'IIIF_Files/' + p

def runutil(oc, file_info, result):
    for entry in oc.list(file_info.get_path()):
        if entry.get_name() == 'queue'
            oc.delete(entry)
            os.utime("workflowautomator/utilities/" + result)
            oc.put_file(file_info, "workflowautomator/utilities/" + result)
            break

username = "ldr_oc_admin"
password = ocpassword
oc = owncloud.Client('https://s3.lib.uchicago.edu/owncloud')
oc.login(username, password)

r = requests.get('https://www2.lib.uchicago.edu/keith/tmp/cai.json')
r = r.json()
allqueues = r['queue']
allqueuesfiltered = []
for rt in allqueues:
    allqueuesfiltered = alqueuessfiltered + filterbottom(rt)

with open('workflowautomator/data/errsnar.json', "r") as jsonfile:
        fjson = json.load(jsonfile)
errors = fjson['errors']

for rt in allqueuesfiltered:
    freshbatcherrors = mainvalidate(oc, rt)
    if not freshbatcherrors:
        runutil(oc, oc.file_info(rt), "valid")
    else:
        runutil(oc, oc.file_info(rt), "invalid")
        errors = errors + freshbatcherrors

jsonwrap = {'errors' : errors}
with open('workflowautomator/data/errsnar.json', "w") as jsonfile:
        json.dump(jsonwrap, jsonfile)