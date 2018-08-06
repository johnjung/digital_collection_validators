from listpage.timess import *
from listpage.models import *

def integratetimess(timess):
	'''
	Takes information in server update list and applies it
	to mvolFolder objects in site
	'''
	if timess.servername == "development":
		for line in timess.lists["uploaded"]:
			target = mvolFolder.objects.get(name = line[0])
			target.dev = line[1]
			target.save()
	if timess.servername == "production":
		for line in timess.lists["uploaded"]:
			target = mvolFolder.objects.get(name = line[0])
			target.pro = line[1]
			target.save()

def integrateot(namey, date, servertype):
	target = mvolFolder.objects.get(name = namey)
	if(servertype == "development"):
		print("development, initially:")
		print(target.dev)
		print(target.pro)
		target.dev = date
		print("development, after changing")
		print(target.dev)
		print(target.pro)
		target.save()
	if(servertype == "production"):
		print("production, initially:")
		print(target.dev)
		print(target.pro)
		target.pro = date
		print("production, after changing")
		print(target.dev)
		print(target.pro)
		target.save()

def integratetimesx(timess):
	for line in timess.lists["uploaded"]:
		integrateot(line[0], line[1], timess.servername)