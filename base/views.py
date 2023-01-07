#importing modules
from django.shortcuts import render
from django.http import HttpResponse


#view function
def index(request):
    #return HttpResponse("Hello, World!")
    return render(request,"blog/index.html")