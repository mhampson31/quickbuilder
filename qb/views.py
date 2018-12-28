from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Ship
from .forms import RandomListForm
from .tools import random_list


class IndexView(generic.ListView):
    template_name = 'qb/index.html'
    context_object_name = 'ship_list'

    def get_queryset(self):
        return Ship.objects.all()


class ShipView(generic.DetailView):
    model = Ship
    template_name = 'qb/ship.html'


def ship_detail(request, id):
    ship = get_object_or_404(Ship, pk=id)
    return render(request, 'ship_detail.html', {'ship':ship})

def quickbuild_view(request, id_list):
    quickbuilds = id_list.split(',')


def random_quickbuild(request):
    if request.method == 'POST':
        build_list = random_list(threat=int(request.POST['threat']), faction_id=request.POST['faction'])
        form = RandomListForm(request.POST)

    else:
        form = RandomListForm()
        build_list = []
    return render(request, 'qb/random.html', {'form':form, 'build_list':build_list})




