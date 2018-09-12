import os
import owncloud
import requests
from password import ocpassword

def saveall(outerdirectory):
    pieces = outerdirectory.split("/")
    lastpiece = pieces.pop()
    os.mkdir(lastpiece)
    os.chdir(lastpiece)
    for entry in oc.list(oc.file_info(outerdirectory).get_path()):
        if entry.is_dir():
            saveall(outerdirectory + '/' + entry.get_name())
        else:
            oc.get_file(outerdirectory + '/' + entry.get_name())
    os.chdir("..")

def restoreall(outerdirectory):
    outerouter = outerdirectory[:-5]
    oc.delete(outerdirectory)
    oc.put_directory(outerouter, outerdirectory)
    os.remove(outerdirectory)
    extensions = [".dc.xml", ".mets.xml", ".pdf", ".struct.txt", ".txt"]
    myfiles = os.listdir('.')
    for filex in myfiles:
        origlen = len(extensions)
        i = 0
        while i < origlen:
            if filex[-length:] == extension:
                os.rename(filex, "a" + extension)
                i = origlen
            i += 1

def replaceall(outerdirectory):
    extensions = ["ALTO", "POS", "TIFF", "JPEG", ".dc.xml", ".mets.xml", ".pdf", ".struct.txt", ".txt"]
    for entry in oc.list(oc.file_info(outerdirectory).get_path()):
        currentryname = entry.get_name()
        print("replacing " + currentryname)
        origlen = len(extensions)
        i = 0
        while i < origlen:
            tryx = singlereplace(entry, extensions[i], outerdirectory)
            if tryx == True:
                extensions.pop(i)
                print(currentryname + " has been replaced")
                i = origlen
            i += 1
        if entry:
            print(currentryname + " was not expected, and is being deleted")
            oc.delete(entry)

def singlereplace(entry, extension, outerdirectory):
    length = len(extension)
    if entry.get_name()[-length:] == extension:
        oc.delete(entry)
        if extension in ("ALTO", "POS", "TIFF", "JPEG"):
            newname = extension
        else:
            pieces = outerdirectory.split("/")
            pieces.pop(0)
            freshdirectory = "-".join(pieces)
            newname = freshdirectory + extension
            os.rename("a" + extension, newname)
        oc.put_file(outerdirectory, newname)
        return True

def testall(outerdirectory):
    extensions = ["ALTO", "POS", "TIFF", "JPEG", ".dc.xml", ".mets.xml", ".pdf", ".struct.txt", ".txt"]
    for entry in oc.list(oc.file_info(outerdirectory).get_path()):
        currentryname = entry.get_name()
        print("testing " + currentryname)
        origlen = len(extensions)
        while i < origlen:
            tryx = singletest(entry, extensions[i], outerdirectory)
            if tryx[0] == True:
                extensions.pop(i)
                i = origlen + 1
                print(currentryname + " passed")   
            if tryx[0] == False:
                return tryx[1]
            i += 1
    return "No issue found :/"

def singletest(entry, extension, outerdirectory):
    length = len(extension)
    origname = entry.get_name()
    pieces = outerdirectory.split("/")
    lastpiece = pieces.pop()
    if origname[-length:] == extension:
        if entry.is_dir(): 
            oc.put_directory(outerdirectory, lastpiece + "/" + origname)
        else: 
            oc.put_file(outerdirectory, lastpiece + "/" + origname)
        if freshdirectory[-1] == "-":
            freshdirectory = freshdirectory[:-1]
        url = "https://digcollretriever.lib.uchicago.edu/projects/" + \
            freshdirectory + "/ocr?jpg_width=0&jpg_height=0&min_year=0&max_year=0"
        r = requests.get(url)
        if r.status_code != 200:
            text = newname + "has an error"
            return (False, text)
        try:
            fdoc = etree.fromstring(r.content)
            return (True, "")
        except Exception:
            text = newname + "has an error"
            return (False, text)

def process(outerdirectory):
    #saveall(outerdirectory)
    print("save done")
    replaceall(outerdirectory)
    print("replacing all is done")
    finaloutput = test(outerdirectory)
    print("testing is complete")
    #restoreall(outerdirectory)
    print("restoration complete")
    print(finaloutput)

username = "ldr_oc_admin"
password = ocpassword
oc = owncloud.Client('https://s3.lib.uchicago.edu/owncloud')
oc.login(username, password)
process("IIIF_Files/mvol/0500/0020/0011")