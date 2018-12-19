from django.shortcuts import HttpResponse, render

def index(request):
    return HttpResponse("This will be the builder.")
