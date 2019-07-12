import csv
import io
import os
import owncloud
import paramiko
import re
import requests
import sys
import stat

from lxml import etree


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('s3.lib.uchicago.edu', username='ksong814')
ftp = ssh.open_sftp()
check = 'apf1'
path = "/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/apf/1"
print(ftp.listdir(path))

