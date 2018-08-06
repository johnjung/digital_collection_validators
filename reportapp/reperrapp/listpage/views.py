from django.shortcuts import render
from django.http import HttpResponse
from listpage.multilist import *
from listpage.multilistxtract import *
from listpage.models import mvolFolder
import html

# Create your views here.

def main(request):
	context = {'allists' : exmultilist.lists}
	return render(request, 'listpage/main.html', context)

def hierarch(request, mvolfolder_name):
	target = mvolFolder.objects.get(name = mvolfolder_name)
	
	parentlist = []
	curr = target
	namesections = mvolfolder_name.split("/")
	finalchunk = namesections.pop()
	i = len(namesections) - 1
	while(curr.parent):
		parentlist = [(curr.parent, namesections[i] + '/')] + parentlist
		curr = curr.parent
		i -= 1
	
	prelist = target.children.all()
	prelist = prelist.extra(order_by = ['name'])
	childlist = []

	check = html.unescape("&#10004;")
	ex = html.unescape("&#10006;")
	for child in prelist:
		valid = ex
		devsync = ex
		prosync = ex
		if child.valid:
			valid = check
		if child.dev:
			if child.date < child.dev:
				devsync = check
		if child.pro:
			if child.date < child.pro:
				prosync = check
		childlist.append((child, valid, devsync, prosync))


	for i in childlist:
		print(i[0].name)
	context = {'name' : (mvolfolder_name, finalchunk),
						'parents' : parentlist,
						'children' : childlist}
	
	return render(request, 'listpage/mvolpage.html', context)