import paramiko
import hashlib

host = "ftp.coginvasion.com"
port = 22
transport = paramiko.Transport((host, port))

password = "toontownTf2!"
username = "coginvas"
transport.connect(username = username, password = password)

sftp = paramiko.SFTPClient.from_transport(transport)

print 'Sucessfully opened sftp connection!'

# Let's take the file_info.txt and turn it into file_info_old.txt
file_info = open('file_info.txt', 'r')
file_info_old = open('file_info_old.txt', 'w')
file_info_old.write(file_info.read())
file_info_old.flush()
file_info_old.close()

filesToUpload = []

file_info.seek(0)
for line in file_info.readlines():
    if not "//" in line:
        filename, sha = line.split(' ')
        if hashlib.sha1()
