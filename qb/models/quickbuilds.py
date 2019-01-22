# encoding: UTF-8

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.safestring import mark_safe
from django.utils.functional import cached_property

from .cards import Pilot, Faction, Upgrade


class QBLimited(models.Model):
    # This model is used to access the qb_limited_view in the DB.
    # The purpose of that view is to offload some of the repetitive queries done by the limited checks when assembling
    # random quickbuild lists.
    quickbuild_id = models.IntegerField(primary_key=True)
    faction = models.ForeignKey(Faction, on_delete=models.DO_NOTHING)
    threat = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=120, null=True, blank=True)
    limited = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'qb_limited_v'


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
            name.append(p.name + ' (' + p.ship.name + ')')
        self.name = ' and '.join(name)

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
    def agility(self): return self.make_stat('agility')

    @property
    def shields(self): return self.make_stat('shields')

    @property
    def hull(self): return self.make_stat('hull')


    @property
    def force(self):
        # Force is on the pilot, unlike other stats, so the make_stat method won't work
        return self.pilot.force + sum([u.force for u in self.upgrades.filter(force__gt=0)])
