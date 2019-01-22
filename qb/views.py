import re, logging

from random import choice

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.db.models import Count, Max, prefetch_related_objects

from .models import Ship, QuickBuild, Faction, Build, QBLimited
from .forms import RandomListForm


logger = logging.getLogger(__name__)

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
        #prefetch_related_objects(qb_list, 'build_set__upgrades') #probably need to go deeper here
        id_param = ID_SEP.join([str(qb.id) for qb in qb_list])
        form = RandomListForm(request.POST)
    else:
        form = RandomListForm()
        qb_list = []
        id_param = None
    return render(request, 'qb/random.html', {'form':form, 'qb_list':qb_list, 'id_param':id_param})


# ####### QuickList functionality ###### #


class QuickList(object):
    def __init__(self, max_threat, faction_id, build_objs=[], build_ids=[]):
        self.max_threat = max_threat
        self.faction_id = faction_id
        self.build_list = [] # a list of QuickBuild objects
        self.rejects = []

        self.ltd_values = {}

        # build_objs could be used to pass already-created QuickBuild objects into the build list, avoiding a DB query.
        # at the moment, these bypass limited checks
        for new_build in build_objs:
            self.add_build(new_build)

        # build_ids is similar to build_objs, except it's a just ID numbers.
        # we can't use id__in=build_ids because that will dedupe, and we want to allow dupes
        for id in build_ids:
            self.add_build(QuickBuild.objects.get(id=id))

    @property
    def threat(self):
        return sum([b.threat for b in self.build_list])

    def random_fill(self):
        threat = self.max_threat - self.threat
        all_builds = QuickBuild.objects.filter(faction_id=self.faction_id).filter(threat__lte=threat)
        all_limited = QBLimited.objects.filter(faction_id=self.faction_id).filter(threat__lte=threat)
        rejects = []

        while threat > 0:
            rejected = False
            try:
                b = choice([b for b in all_builds if b.threat <= threat and b.id not in rejects])
            except IndexError:  # random.choice raises this exception if new_build is empty
                logging.info('No ships left with threat <= {}'.format(threat))
                break
            limited_names = all_limited.filter(quickbuild_id=b.id).values('name', 'limited').annotate(count=Count('name'))
            for name in limited_names:
                if name['limited'] and self.limited_violation(name):
                    rejects.append(b.id)
                    rejected = True
                    break
            if rejected:
                continue
            else:
                self.add_build(b, lnames=limited_names)
                threat = self.max_threat - self.threat
                logging.info('{} remaining threat points to spend.'.format(threat))

    def add_build(self, new_build, lnames=None):
        # new_build: a QuickBuild object
        self.build_list.append(new_build)
        if not lnames:
            lnames = QBLimited.objects.filter(quickbuild_id=new_build.id).values('name', 'limited').annotate(count=Count('name'))
        for name in lnames:
            if name['name'] not in self.ltd_values:
                self.ltd_values[name['name']] = 0
            self.ltd_values[name['name']] += name['count']


    def limited_violation(self, name):
        # card is a single dict containing name, limited, and count(name), as from random_fill
        # return True if adding this name would violate the limited value
        existing_count = self.ltd_values.get(name['name'], 0)
        if existing_count + name['count'] > int(name['limited']):
            return True
        else:
            return False

