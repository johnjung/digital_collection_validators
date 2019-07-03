import logging
import paramiko

logging.basicConfig()
logging.getLogger("paramiko").setLevel(logging.WARNING)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('s3.lib.uchicago.edu', username='ksong814', password='')


