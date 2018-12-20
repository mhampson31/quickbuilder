from django.shortcuts import HttpResponse, render
from django.template import loader

from .models import Ship

def index(request):
    ship_list = Ship.objects.all()
    template = loader.get_template('ship/index.html')
    context = {
        'ship_list': ship_list,
    }
    return HttpResponse(template.render(context, request))


def ship(request, id):

    return HttpResponse("Here is ship {}".format(id))
