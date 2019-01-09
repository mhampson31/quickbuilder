# encoding: UTF-8

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.safestring import mark_safe

from qb.templatetags.qb_extras import get_icon

from .choices import SIZE_CHOICES, UPGRADE_CHOICES
from .base import Card, Stats, Charges, Action, ActionMixin, Attack, Faction


class Ship(Card, Stats):
    size = models.CharField(max_length=1, choices=SIZE_CHOICES, default='S')
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    ability_title = models.CharField(max_length=32, blank=True, default='')
    limited = None
    cost=None

    def all_actions(self):
        return [s.display_name for s in self.shipaction_set.all()]

    @property
    def icon(self):
        return mark_safe('<i class="xwing-miniatures-ship xwing-miniatures-ship-{}"></i>'.format(self.xws))

    class Meta:
        ordering = ['name']
        unique_together = ('xws', 'faction')


class ShipAction(ActionMixin, models.Model):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    hard = models.BooleanField(default=False)
    linked_action = models.ForeignKey(Action, related_name='linked_ship_action',
                                      on_delete=models.CASCADE, null=True, blank=True, default=None)
    linked_hard = models.BooleanField(default=False)


class ShipAttack(Attack):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE)
    type = 'primary'


class Pilot(Card, Charges):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE)
    caption = models.CharField(max_length=100, blank=True)
    droid = models.BooleanField(default=False)
    initiative = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(6)]
     )

    @property
    def faction(self):
        return self.ship.faction.name

    @property
    def actions(self):
        aset = self.ship.shipaction_set.all()
        if self.droid:
            focus = Action.objects.get(name='Focus')
            calc = Action.objects.get(name='Calculate')
            new_aset = []
            for a in aset:
                if a.action == focus or a.linked_action == focus:
                    a1 = calc if a.action == focus else a.action
                    a2 = calc if a.linked_action == focus else a.linked_action
                    new_aset.append(ShipAction(action=a1, hard=a.hard, linked_action=a2, linked_hard=a.linked_hard))
                else:
                    new_aset.append(a)
            aset = new_aset
        return aset


class Upgrade(Card, Stats, Charges):
    slot = models.CharField(max_length=3, choices=UPGRADE_CHOICES)
    slot2 = models.CharField(max_length=3, choices=UPGRADE_CHOICES, null=True, blank=True, default=None)

    #Two-sided upgrades just link to another upgrade for the reverse side.
    side2 = models.OneToOneField('self', null=True, blank=True, default=None, on_delete=models.CASCADE)
    actions = models.ManyToManyField(Action, through='UpgradeAction', through_fields=('upgrade', 'action'))

    @property
    def grants(self):
        stats = []
        if self.shields:
            stats.append('+{} <span class="shields">[Shield]</span>'.format(self.shields))
        if self.hull:
            stats.append('+{} <span class="hull">[Hull]</span>'.format(self.hull))
        if self.agility:
            stats.append('+{} <span class="agility">[Agility]</span>'.format(self.agility))
        if self.force:
            stats.append('+{} <span class="force">[Forcecharge]</span>'.format(self.force))
        return '  '.join(stats)

    class Meta:
        ordering = ['slot', 'slot2', 'name']


class UpgradeAction(ActionMixin, models.Model):
    upgrade = models.ForeignKey(Upgrade, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    hard = models.BooleanField(default=False)
    linked_action = models.ForeignKey(Action, related_name='linked_upgrade_action',
                                      on_delete=models.CASCADE, null=True, blank=True, default=None)
    linked_hard = models.BooleanField(default=False)


class UpgradeAttack(Attack):
    upgrade = models.OneToOneField(Upgrade, on_delete=models.CASCADE, related_name='special_attack')
    type = 'special'