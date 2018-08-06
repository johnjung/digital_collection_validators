from django.shortcuts import render
from django.http import HttpResponse
from listpage.multilist import *
from listpage.multilistxtract import *
from listpage.models import mvolFolder

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
	context = {'name' : mvolfolder_name,
						'finalpiece' : finalchunk,
						'parents' : parentlist,
						'children' : target.children.all()}
	return render(request, 'listpage/mvolpage.html', context)