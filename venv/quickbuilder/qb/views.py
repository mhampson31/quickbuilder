from django.shortcuts import HttpResponse, render
from django.template import loader

from .models import Ship
from .tool import random_list

def index(request):
    ship_list = Ship.objects.all()
    context = {
        'ship_list': ship_list,
    }
    return render(request, 'ship/index.html', context )


def random(request):



def ship(request, id):

    return HttpResponse("Here is ship {}".format(id))
