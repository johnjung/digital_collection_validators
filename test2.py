import getpass
import paramiko
import socket
import sys 

host = 's3.lib.uchicago.edu' 
port = 22
family = 0 
type = 0 
proto = 0 
flags = 0 

res = socket.getaddrinfo(host, port, family, type, proto, flags)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# in connect(), if username is not set it defaults to the current local user. 
print('Current local user: ' + getpass.getuser())

# s3 is set up to allow authentication by public key. On a unix-like system, do
# eval `ssh-agent` followed by ssh-add. On a Windows machine, do eval
# "$(ssh-agent -s)" followed by ssh-add. To check if the SSH agent is running,
# echo $SSH_AGENT_PID. 

# try running 'pip freeze' to see what version paramiko is at. (current version
# is 2.6.0)

ssh.connect('s3.lib.uchicago.edu', username='ksong814')

ftp = ssh.open_sftp()