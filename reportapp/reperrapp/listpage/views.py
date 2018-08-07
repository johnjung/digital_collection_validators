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
	
	def retrievevalsyn(child):
		#recursively tells if upper levels in hierarchy are completely
		# valid and synced
		potentialchildren = child.children.all()
		link = False
		if potentialchildren:
			link = True
			valid = check
			devsync = check
			prosync = check
			lastdev = None
			lastpro = None
			child.valid = True
			for grandchild in potentialchildren:
				info = retrievevalsyn(grandchild)
				if grandchild.date > child.date:
					child.date = grandchild.date
				if info[1] == ex:
					valid = ex
					child.valid = False
				if info[2] == ex:
					devsync = ex
				if info[3] == ex:
					prosync = ex
				if lastdev and grandchild.dev:
					if grandchild.dev > lastdev:
						lastdev = grandchild.dev
				else:
					if grandchild.dev:
						lastdev = grandchild.dev
				if lastpro and grandchild.pro:
					if grandchild.pro > lastpro:
						lastpro = grandchild.pro
				else:
					if grandchild.pro:
						lastpro = grandchild.pro
			if devsync == check:
				child.dev = lastdev
			if prosync == check:
				child.pro = lastpro
			child.save()
		else:
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
		return(child, valid, devsync, prosync, link)

	for child in prelist:
		childlist.append(retrievevalsyn(child))
	context = {'name' : (mvolfolder_name, finalchunk),
						'parents' : parentlist,
						'children' : childlist,
	}
	
	return render(request, 'listpage/mvolpage.html', context)