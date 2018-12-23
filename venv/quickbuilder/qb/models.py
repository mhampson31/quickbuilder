from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


# I'm defining this choice list a little differently, because I need to use the full descs later.
# This keeps them available.


SIZE_TYPES = {
    'Small': 'S',
    'Medium': 'M',
    'Large': 'L'
}

UPGRADE_TYPES = {
    'Astromech':'AST',
    'Cannon': 'CNN',
    'Configuration': 'CNF',
    'Crew': 'CRW',
    'Device': 'DVC',
    'Force Power': 'FRC',
    'Gunner': 'GNR',
    'Illicit': 'ILC',
    'Missile': 'MSL',
    'Modification': 'MOD',
    'Sensor':'SNS',
    'Tactical Relay': 'TAC',
    'Talent': 'TLN',
    'Tech': 'TCH',
    'Title': 'TTL',
    'Torpedo':'TRP',
    'Turret':'TRT',
    'Ship':'SHP'
}

SIZE_CHOICES = [(v, k) for k, v in SIZE_TYPES.items()]
UPGRADE_CHOICES = [(v, k) for k, v in UPGRADE_TYPES.items()]

LIMITED_CHOICES = (
    ('1', '•'),
    ('2', '••'),
    ('3', '•••')
)


DIFFICULTY_CHOICES = (
    ('r', 'Red'),
    ('w', 'White'),
    ('b', 'Blue')
)

def make_lnames():
    from .models import LIMITED_CHOICES
    lnames = {}
    for k in LIMITED_CHOICES:
        lnames[k[0]] = []
    return lnames

# base and component classes

class Card(models.Model):
    name = models.CharField(max_length=64)
    xws = models.CharField(max_length=64)
    ffg = models.PositiveIntegerField(blank=True, null=True, default=None)
    limited = models.CharField(max_length=1, choices=LIMITED_CHOICES, blank=True, default='')
    ability = models.CharField(max_length=320, blank=True, default='')
    ability_title = models.CharField(max_length=32, blank=True, default='')

    @property
    def display_name(self):
        if self.limited == '0' or self.limited is None:
            return self.name
        else:
            return '{} {}'.format(self.get_limited_display(), self.name)

    def __str__(self):
        return self.display_name

    class Meta:
        abstract = True
        ordering = ['name']


class Action(models.Model):
    name = models.CharField(max_length=14)
    description = models.CharField(max_length=100)
    icon = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    def display(self, red=False):
        return '<i class="xwing-miniatures-font xwing-miniatures-font-{}{}"></i>'.format(self.icon, ' hard' if red else '')

# ### core models

class Faction(Card):
    limited = None
    ability = None
    cost = None
    ability_title = None
    released = models.BooleanField(default=True)


class Ship(Card):
    size = models.CharField(max_length=1, choices=SIZE_CHOICES, default='S')
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    limited = None
    actions = models.ManyToManyField(Action,
                                     through='ShipAction',
                                     through_fields=('ship', 'action'))
    cost=None

    def all_actions(self):
        return [s.display_name for s in self.shipaction_set.all()]

    class Meta:
        ordering = ['name']
        unique_together = ('xws', 'faction')


class ActionMixin(object):
    """Mixin to permit some common action tasks.
       Assumes any class that uses this will have some action-based attributes"""

    def __str__(self):
        if self.linked_action:
            return '{}->{}'.format(self.action.name, self.linked_action.name)
        else:
            return self.action.name

    @property
    def display_name(self):
        if self.linked_action:
            return '{}->{}'.format(self.action.display(self.hard), self.linked_action.display(self.linked_hard))
        else:
            return self.action.display(self.hard)


class PilotAction(ActionMixin, models.Model):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    hard = models.BooleanField(default=False)
    linked_action = models.ForeignKey(Action, related_name='linked_ship_action',
                                      on_delete=models.CASCADE, null=True, blank=True, default=None)
    linked_hard = models.BooleanField(default=False)


class Pilot(Card):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE)
    caption = models.CharField(max_length=100, blank=True)
    initiative = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(6)]
     )

    @property
    def faction(self):
        return self.ship.faction.name


class Upgrade(Card):
    slot = models.CharField(max_length=3, choices=UPGRADE_CHOICES)
    slot2 = models.CharField(max_length=3, choices=UPGRADE_CHOICES, null=True, blank=True, default=None)
    ability2 = models.CharField(max_length=320, blank=True, default='')
    ability2_title = models.CharField(max_length=32, blank=True, default='')
    actions = models.ManyToManyField(Action, through='UpgradeAction', through_fields=('upgrade', 'action'))

    @property
    def get_both_slots_display(self):
        if self.slot2:
            return '/'.join([self.get_slot_display(), self.get_slot2_display()])
        else:
            return self.get_slot_display()

    def side_actions(self, side):
        return self.upgradeaction_set.filter(side=side)

    @property
    def side_actions_1(self):
        return self.side_actions(1)

    @property
    def side_actions_2(self):
        return self.side_actions(2)


class UpgradeAction(ActionMixin, models.Model):
    side = models.IntegerField(default=1)
    upgrade = models.ForeignKey(Upgrade, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    hard = models.BooleanField(default=False)
    linked_action = models.ForeignKey(Action, related_name='linked_upgrade_action',
                                      on_delete=models.CASCADE, null=True, blank=True, default=None)
    linked_hard = models.BooleanField(default=False)


class QuickBuild(models.Model):
    threat = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)]
     )
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    pilots = models.ManyToManyField(Pilot,
                                    through='Build',
                                    through_fields=('quickbuild', 'pilot'))

    @property
    def pilot_names(self):
        return '; '.join([p.name for p in self.pilots.all()])

    @property
    def limited_names(self):
        # QuickBuilds and Builds have a similar property, used to collect any limited pilots/upgrades in use
        lnames = make_lnames()
        for b in self.build_set.all():
            bnames = b.limited_names
            for k in lnames:
                lnames[k].extend(bnames[k])
        return lnames

    def __str__(self):
        return '{} ({})'.format(self.pilot_names, self.threat)


class Build(models.Model):
    quickbuild = models.ForeignKey(QuickBuild, on_delete=models.CASCADE)
    pilot = models.ForeignKey(Pilot, related_name='qb_pilot_id', on_delete=models.CASCADE)
    upgrades = models.ManyToManyField(Upgrade, blank=True, related_name='upgrade_id')

    def __str__(self):
        return self.pilot.name

    @property
    def limited_names(self):
        # QuickBuilds and Builds have a similar property, used to collect any limited pilots/upgrades in use
        lnames = make_lnames()
        cards = [u for u in self.upgrades.all() if u.limited not in ('0', '')]
        if self.pilot.limited not in ('0', ''):
            cards.append(self.pilot)

        for c in cards:
            lnames[c.limited].append(c.name)

        return lnames

    @property
    def all_actions(self):
        actions = [a for a in self.pilot.ship.shipaction_set.all()]
        upgrade_actions = []
        for upgrade in self.upgrades.all():
            if upgrade.upgradeaction_set.all():
                actions.extend([a for a in upgrade.upgradeaction_set.all()])
        return actions

