from django.shortcuts import render
from django.http import HttpResponse
from listpage.multilist import *
from listpage.multilistxtract import *
from listpage.models import mvolFolder
import html
import json
import datetime
import time
import pytz

# Create your views here.

def main(request):
	context = {'allists' : exmultilist.lists}
	return render(request, 'listpage/main.html', context)

def hierarch(request, mvolfolder_name):

	def chxistnrecent(currtime, comparetime):
		# checks if two times exist and compares them
		checkd = html.unescape("&#10004;")
		exd = html.unescape("&#10006;")
		if comparetime:
			if comparetime < currtime:
				return exd
			else:
				return checkd
		else:
			return None

	def chxistnrecentx(status):
		# checks if two times exist and compares them
		checkd = html.unescape("&#10004;")
		exd = html.unescape("&#10006;")
		if status == "in-sync":
			return checkd
		elif status == "out-of-sync":
			return exd
		else:
			return None

	def localize(child):
		timezone = pytz.timezone("America/Chicago")	
		try:
			child[1]['owncloud'][1] = timezone.localize(datetime.datetime.fromtimestamp(child[1]['owncloud'][1]))
		except Exception:
			pass
		try:
			child[1]['development'][1] = timezone.localize(datetime.datetime.fromtimestamp(child[1]['development'][1]))
		except Exception:
			pass
		try:
			child[1]['production'][1] = timezone.localize(datetime.datetime.fromtimestamp(child[1]['production'][1]))
		except Exception:
			pass


	currname = mvolfolder_name
	namesections = mvolfolder_name.split("-")
	finalchunk = namesections.pop()

	parentlist = []
	namehold = ""
	first = True
	with open('listpage/snar.json', "r") as jsonfile:
		fjson = json.load(jsonfile)

	currdir = fjson

	for subsect in namesections:
				if first:
					namehold = subsect
					first = False
				else:
					namehold = namehold + "-" + subsect
				parentlist.append((namehold, subsect))
				try:
					currdir = currdir[namehold]['children']
				except Exception as e:
					break
	if mvolfolder_name == "mvol":
			prechildlist = currdir['mvol']['children']
	else:
		namehold = namehold + "-" + finalchunk
		try:
			prechildlist = currdir[namehold]['children']
		except Exception as e:
			prechildlist = {}
	childlist = []
	i = 0
	childnames = prechildlist.keys()
	check = html.unescape("&#10004;")
	ex = html.unescape("&#10006;")
	for child in prechildlist.items():
		valid = ex
		prosync = ex
		devsync = ex
		localize(child)		
		currtime = child[1]['owncloud'][1]
		devsync = chxistnrecentx(child[1]['development'][0])
		prosync = chxistnrecentx(child[1]['production'][0])
		if child[1]['owncloud'][0] == "valid":
			valid = check
		childlist.append((list(childnames)[i], child, valid, devsync, prosync))
		i += 1

	oneupfrombottom = False
	if childlist:
		if not 'children' in childlist[0][1][1]:
			oneupfrombottom = True

	context = {'name' : (currname, finalchunk),
						'parents' : parentlist,
						'children' : childlist,
						'oneupfrombottom' : oneupfrombottom,
	}
	
	return render(request, 'listpage/mvolpagejson.html', context)