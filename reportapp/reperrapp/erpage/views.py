from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def mainpage(request):
    errors = ["This thing was bad.",
              "This other thing was even worse.",
              "Whoa, slow down now, what is this."]
    context = {'errarray' : errors}
    return render(request, 'erpage/mainpage.html', context)
