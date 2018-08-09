from listpage.multilist import *
from listpage.models import mvolFolder
import json
import re
import datetime
import time
import pytz

def addmvolFolder(namey, datey, parentnamey):
	#Creates new mvolFolder based on given name, date, and parent mvolFolder
	new = mvolFolder(name = namey, date = datey)
	parent = mvolFolder.objects.get(name = parentnamey)
	#print(new.date)
	new.save()

def updatedate(namey, datey):
	#Called on folder when change is being made in subfolder. If the change is
	# associated with a more recent date, the folder should update its own date
	targmvolFolder = mvolFolder.objects.get(name = namey)
	targdate = targmvolFolder.date
	timezone = pytz.timezone("America/Chicago")
	try:	
		datey = datetime.datetime.fromtimestamp(datey/1000)
	except Exception as e:
		datey = datetime.datetime.fromtimestamp(datey)
	datey = timezone.localize(datey)
	if targdate == None:
		targmvolFolder.date = datey
		targmvolFolder.save()
	elif datey > targdate:
		targmvolFolder.date = datey
		targmvolFolder.save()

def addmvolFolderunixtime(namey, datey, parentnamey):
	#Creates new mvolFolder based on given name, date, and parent mvolFolder
	timezone = pytz.timezone("America/Chicago")
	try:	
		snar = datetime.datetime.fromtimestamp(datey/1000)
	except Exception as e:
		snar = datetime.datetime.fromtimestamp(datey)
	datey = timezone.localize(snar)
	new = mvolFolder(name = namey, date = datey, 
	parent = mvolFolder.objects.get(name = parentnamey))
	new.save()

def imultifjson(jsonfile):
	with open(jsonfile, "r") as jsonfile:
		fjson = json.load(jsonfile)
	integratemultilistunixtime(multilist(fjson["none"], fjson["ready"], fjson["queue"],
		fjson["valid"], fjson["invalid"]))

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
			#print(trydate)
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

def integratemultilistunixtime(multilist):
	'''
	Takes all information in given multilist, and creates or
	updates relevant mvolFolder objects. Because of issues with
	parent folders, this will assume that a mvol folder already
	exists
	'''
	if mvolFolder.objects.filter(name = "mvol").count() == 0:
		xyz = mvolFolder(name = "mvol")
		xyz.save()
	for key in multilist.lists:
		for line in multilist.lists[key]:
			trydate = line[1]
			tryname = line[0]
			#print(trydate)
			#print(tryname)
			#print(datetime.datetime.fromtimestamp(trydate/1000))
			namesections = tryname.split("-")
			namehold = ""
			first = True
			upperparent = "mvol"
			for subsect in namesections:
				#print(subsect)
				if first:
					namehold = subsect
					first = False
				else:
					namehold = namehold + "-" + subsect
				if mvolFolder.objects.filter(name = namehold).count() > 0:
					upperparent = namehold
					updatedate(namehold, trydate)
				else:
					#print("about to add")
					addmvolFolderunixtime(namehold, trydate, upperparent)
				upperparent = namehold
			targmvolFolder = mvolFolder.objects.get(name = tryname)
			if key == "invalid":
				targmvolFolder.valid = False
			targmvolFolder.date = trydate