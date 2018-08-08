from listpage.timess import *
from listpage.models import *

def integratetimess(timess):
	'''
	Takes information in server update list and applies it
	to mvolFolder objects in site, allowing sync statuses
	to be generated
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