# encoding: UTF-8

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.safestring import mark_safe
from django.utils.functional import cached_property

from .cards import Pilot, Faction, Upgrade
from .base import make_lnames

class QuickBuild(models.Model):
    name = models.CharField(max_length=120, null=True, blank=True)
    threat = models.PositiveSmallIntegerField(db_index=True, validators=[MinValueValidator(1), MaxValueValidator(8)])
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    pilots = models.ManyToManyField(Pilot,
                                    through='Build',
                                    through_fields=('quickbuild', 'pilot'))

    def make_name(self):
        # this method can be deleted once the old names have been converted
        name = []
        for p in self.pilots.all():
            name.append(p.name + '(' + p.ship.name + ')')
        self.name = ' and '.join(name)

    @cached_property
    def limited_names(self):
        lnames = make_lnames()
        for b in self.build_set.prefetch_related('upgrades').select_related('pilot').all():
            cards = list(b.upgrades.filter(limited__gte=1))
            if b.pilot.limited not in ('0', ''):
                cards.append(b.pilot)
            for c in cards:
                lnames[c.limited].append(c.name)
        return lnames

    def __str__(self):
        return '{} ({})'.format(self.name, self.threat)


class Build(models.Model):
    """
    This model is really the core unit of this app. It takes a pilot+ship, maybe some upgrades, and prepares it for
    presentation.
    """
    quickbuild = models.ForeignKey(QuickBuild, on_delete=models.CASCADE)
    pilot = models.ForeignKey(Pilot, related_name='qb_pilot_id', on_delete=models.CASCADE)
    upgrades = models.ManyToManyField(Upgrade, blank=True, related_name='upgrade_id')

    def __str__(self):
        return self.pilot.name

    def make_stat(self, stat):
        """This method lets us add any upgrade benefits to a ship's agility, hull, or shields """
        stat_gt = {'{}__gt'.format(stat): 0}
        return getattr(self.pilot.ship, stat) + sum([getattr(u, stat) for u in self.upgrades.filter(**stat_gt)])

    @property
    def limited_names(self):
        # QuickBuilds and Builds have a similar property, used to collect any limited pilots/upgrades in use
        lnames = make_lnames()
        cards = [u for u in self.upgrades.filter(limited__gte=1)]
        if self.pilot.limited not in ('0', ''):
            cards.append(self.pilot)

        for c in cards:
            lnames[c.limited].append(c.name)

        return lnames

    @property
    def agility(self): return self.make_stat('agility')

    @property
    def shields(self): return self.make_stat('shields')

    @property
    def hull(self): return self.make_stat('hull')


    @property
    def force(self):
        # Force is on the pilot, unlike other stats, so the make_stat method won't work
        return self.pilot.force + sum([u.force for u in self.upgrades.filter(force__gt=0)])
