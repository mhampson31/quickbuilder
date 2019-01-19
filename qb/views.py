from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic

from .models import Ship, QuickBuild, Faction
from .forms import RandomListForm
from .tools import QuickList

import re

ID_SEP = '-'

id_rx = re.compile(r'\d+')


class IndexView(generic.ListView):
    template_name = 'qb/index.html'
    context_object_name = 'faction_list'

    def get_queryset(self):
        return Faction.objects.all()


class ShipView(generic.DetailView):
    model = Ship
    template_name = 'qb/ship.html'


def faction_builds(request, faction):
    faction = Faction.objects.values('id', 'name').get(xws=faction)
    builds = QuickBuild.objects.filter(faction_id=faction['id']).order_by('-threat')
    return render(request, 'qb/faction_builds.html', {'faction':faction['name'], 'builds':builds})


def qb_detail(request, qb_id):
    qb = QuickBuild.objects.get(id=qb_id)
    return render(request, 'qb/qb_list.html', {'qb_list':(qb, )})


def ship_detail(request, id):
    ship = get_object_or_404(Ship, pk=id)
    return render(request, 'ship_detail.html', {'ship':ship})


def quickbuild_list(request, qb_list):
    id_list = qb_list.split(ID_SEP)
    qb_lookup = {}
    # a simple IN would dedupe, so we have an extra step in our selection
    for q in list(QuickBuild.objects.filter(id__in=id_list)):
        qb_lookup[q.id] = q
    qb_list = [qb_lookup[int(i)] for i in id_list]
    return render(request, 'qb/qb_list.html', {'qb_list':qb_list, 'id_list':id_list})


def random_quickbuild(request):
    if request.method == 'POST':
        ql = QuickList(max_threat=int(request.POST['threat']), faction_id=request.POST['faction'])
        ql.random_fill()
        qb_list = ql.build_list
        id_param = ID_SEP.join([str(qb.id) for qb in qb_list])
        form = RandomListForm(request.POST)
    else:
        form = RandomListForm()
        qb_list = []
        id_param = None
    return render(request, 'qb/random.html', {'form':form, 'qb_list':qb_list, 'id_param':id_param})




