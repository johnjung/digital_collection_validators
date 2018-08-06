from listpage.multilist import *
from listpage.models import mvolFolder
import re

def addmvolFolder(namey, datey, parentnamey):
	#Creates new mvolFolder based on given name, date, and parent mvolFolder
	new = mvolFolder(name = namey, date = datey, 
	parent = mvolFolder.objects.get(name = parentnamey))
	new.save()

def updatedate(namey, datey):
	#Called on folder when change is being made in subfolder. If the change is
	# associated with a more recent date, the folder should update its own date
	targmvolFolder = mvolFolder.objects.get(name = namey)
	targdate = targmvolFolder.date
	if targdate == None:
		targmvolFolder.date = datey
		targmvolFolder.save()
	elif datey > targdate:
		targmvolFolder.date = datey
		targmvolFolder.save()

def integratemultilist(multilist):
	'''
	Takes all information in given multilist, and creates or
	updates relevant mvolFolder objects. Because of issues with
	parent folders, this will assume that a mvol folder already
	exists
	'''
	for key in multilist.lists:
		for line in multilist.lists[key]:
			trydate = line[1]
			tryname = line[0]
			print(trydate)
			print(tryname)
			namesections = tryname.split("/")
			namehold = ""
			first = True
			upperparent = "mvol"
			for subsect in namesections:
				print(subsect)
				if first:
					namehold = subsect
					first = False
				else:
					namehold = namehold + "/" + subsect
				if mvolFolder.objects.filter(name = namehold).count() > 0:
					upperparent = namehold
				else:
					print("about to add")
					addmvolFolder(namehold, trydate, upperparent)
				upperparent = namehold
			targmvolFolder = mvolFolder.objects.get(name = tryname)
			if key == "invalid":
				targmvolFolder.valid = False
			targmvolFolder.date = trydate