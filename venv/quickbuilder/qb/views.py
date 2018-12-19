from django.shortcuts import HttpResponse, render

def index(request):
    return HttpResponse("This will be the builder.")

def view_ship(request, ffg):
    return True