from django.shortcuts import render
from django.http import HttpResponse
import html
import json
import datetime
import time
import pytz

# Create your views here.


def localizer(target, mode):
    '''Convert unix timestamps to localized python datetime.datetime objects.
       Arguments:
           target: if mode is "list": a list of tuples, where each tuple contains two elements:
               first, the state of a given item, and second, the time as
                   seconds since the unix epoch. if mode is "hierarch": a single directory dict
           mode: "hierarch" or "list" indicating which localize section is to be used
       Side effect:
       the second element of each tuple is converted to a python
           datetime.datetime object.
    '''
    timezone = pytz.timezone("UTC")
    if mode == "list":
        for t in target:
            t[1] = timezone.localize(datetime.datetime.fromtimestamp(t[1]))
    elif mode == "hierarch":
        for s in ('owncloud', 'development', 'production'):
            try:
                target[s][1] = timezone.localize(
                    datetime.datetime.fromtimestamp(target[s][1]))
            except Exception:
                pass


def homepage(request):
    breadcrumbs = [{
        "href": "/",
        "text": "Home"
    }]
    context = {"breadcrumbs": breadcrumbs}
    return render(request, 'workflowautomator/homepage.html', context)


def errpage(request):
    breadcrumbs = [{
        "href": "/",
        "text": "Home"},
        {"href": "/workflowautomator", "text": "Emil Project Homepage"}]
    with open('workflowautomator/data/errsnar.json', "r") as jsonfile:
        fjson = json.load(jsonfile)
    context = {'errarray': fjson['errors'], "breadcrumbs": breadcrumbs}
    return render(request, 'workflowautomator/errpage.html', context)


def prelistpage(request):

    breadcrumbs = [{"href": "/", "text": "Home"},
                   {"href": "/workflowautomator", "text": "Emil Project Homepage"}]
    with open('workflowautomator/data/listsnar.json', "r") as jsonfile:
        fjson = json.load(jsonfile)
    n = 5
    fjson = {
        "none": (fjson["none"][:n], len(fjson["none"]) > n),
        "ready": (fjson["ready"][:n], len(fjson["ready"]) > n),
        "queue": (fjson["queue"][:n], len(fjson["queue"]) > n),
        "valid": (fjson["valid"][:n], len(fjson["valid"]) > n),
        "invalid": (fjson["invalid"][:n], len(fjson["invalid"]) > n)
    }

    for k, v in fjson.items():
        localizer(v[0], "list")
    context = {"allists": fjson, "breadcrumbs": breadcrumbs}
    return render(request, 'workflowautomator/prelistpage.html', context)


def listpage(request, status):
    breadcrumbs = [{
        "href": "/",
        "text": "Home"},
        {"href": "/workflowautomator", "text": "Emil Project Homepage"},
        {"href": "/workflowautomator/mvolreport", "text": "Mvol Report"}]
    with open('workflowautomator/data/listsnar.json', "r") as jsonfile:
        fjson = json.load(jsonfile)

    localizer(fjson[status], "list")
    context = {"allists": fjson[status],
               "name": status, "breadcrumbs": breadcrumbs}
    return render(request, 'workflowautomator/listpage.html', context)


def hierarch(request, mvolfolder_name):

    def breadcrumbsmaker(mvolfolder_name):
        namesections = mvolfolder_name.split("-")
        breadcrumbs = []
        for i in range(0, len(namesections) - 1):
            breadcrumbs.append({
                "href": "/workflowautomator/" + '-'.join(namesections[: i + 1]),
                "text": namesections[i]})
        return breadcrumbs

    def get_mvol_data(j, mvolfolder_name):
        namesections = mvolfolder_name.split("-")
        currdir = j
        namehold = namesections.pop(0)
        currdir = currdir[namehold]
        for namesect in namesections:
            namehold = '-'.join([namehold, namesect])
            currdir = currdir['children'][namehold]
        return currdir

    breadcrumbs = [{
        "href": "/",
        "text": "Home"},
        {"href": "/workflowautomator", "text": "Emil Project Homepage"}]
    breadcrumbs = breadcrumbs + breadcrumbsmaker(mvolfolder_name)

    finalchunk = mvolfolder_name.split("-").pop()

    with open('workflowautomator/data/snar.json', "r") as jsonfile:
        fjson = json.load(jsonfile)
    prechildlist = get_mvol_data(fjson, mvolfolder_name)['children']
    childlist = []
    check = html.unescape("&#10004;")
    ex = html.unescape("&#10006;")
    for name, child in prechildlist.items():
        # determines where checks, exes, and nones should go for each directory
        valid = ex
        prosync = "none"
        devsync = "none"
        localizer(child, "hierarch")
        currtime = child['owncloud'][1]
        if child['development'][0] == "in-sync":
            devsync = check
        elif child['development'][0] == "out-of-sync":
            devsync = ex
        if child['production'][0] == "in-sync":
            prosync = check
        elif child['production'][0] == "out-of-sync":
            prosync = ex
        if child['owncloud'][0] == "valid":
            valid = check
        childlist.append((name, child, valid, devsync, prosync))

    oneupfrombottom = False
    if childlist:
        if 'children' not in childlist[0][1]:
            oneupfrombottom = True

    context = {'name': (mvolfolder_name, finalchunk),
               'children': childlist,
               'oneupfrombottom': oneupfrombottom,
               'breadcrumbs': breadcrumbs
               }

    return render(request, 'workflowautomator/mvolpagejson.html', context)
