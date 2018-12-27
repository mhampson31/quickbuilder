# encoding: UTF-8

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from .templatetags.qb_extras import get_icon

# todo: is this still in use anywhere?
def get_icon2(iname, red=False):
    return '<span class="icon"><i class="xwing-miniatures-font xwing-miniatures-font-{}{}"></i>'.format(iname.lower(), ' hard' if red else '')

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
    ability = models.CharField(max_length=400, blank=True, default='')
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

    def display(self, css=False):
        return get_icon(self.icon, css)


class Stats(models.Model):
    agility = models.PositiveIntegerField(default=0)
    shields = models.PositiveIntegerField(default=0)
    hull = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True


class Attacks(models.Model):

    front = models.PositiveIntegerField(default=0)
    left = models.PositiveIntegerField(default=0)
    right = models.PositiveIntegerField(default=0)
    rear = models.PositiveIntegerField(default=0)

    full_front = models.PositiveIntegerField(default=0)
    full_rear = models.PositiveIntegerField(default=0)
    bullseye = models.PositiveIntegerField(default=0)
    doubleturret = models.PositiveIntegerField(default=0)
    turret = models.PositiveIntegerField(default=0)

    range = models.CharField(max_length=3, blank=True)

    class Meta:
        abstract = True


class Charges(models.Model):
    force = models.PositiveIntegerField(default=0)
    charge = models.PositiveIntegerField(default=0)
    charge_regen = models.BooleanField(default=False)

    class Meta:
        abstract = True


class ActionMixin(object):
    """Mixin to permit some common action tasks.
       Assumes any class that uses this will have some action-based attributes"""

    def __str__(self):
        if self.linked_action:
            return '{} -> {}'.format(self.action.name, self.linked_action.name)
        else:
            return self.action.name

    def __eq__(self, other):
        """
        We occassionally need to a==b different kinds of upgrades.
        :param other: Another object, ideally using this mixin class
        :return: True if both objects have the same actions and same difficulties.
        """
        try:
            return self.action == other.action and \
               self.hard == other.hard and \
               self.linked_action == other.linked_action and \
               self.linked_hard == other.linked_hard
        except AttributeError:
            return False


    @property
    def display_name(self):
        if self.linked_action:
            return '<span class="border rounded icon">{}{}{}</span>'.format(get_icon(self.action.icon, css='hard' if self.hard else None),
                                     get_icon('linked', css='linked'),
                                     get_icon(self.linked_action.icon, css='hard' if self.linked_hard else None))
        else:
            return '<span class="border rounded icon">{}</span>'.format(get_icon(self.action.icon, css='hard' if self.hard else None))


# ### core models

class Faction(Card):
    limited = None
    ability = None
    cost = None
    ability_title = None
    released = models.BooleanField(default=True)


class Ship(Card, Stats, Attacks):
    size = models.CharField(max_length=1, choices=SIZE_CHOICES, default='S')
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    limited = None
    cost=None

    def all_actions(self):
        return [s.display_name for s in self.shipaction_set.all()]

    @property
    def icon(self):
        return '<i class="xwing-miniatures-ship xwing-miniatures-ship-{}"></i>'.format(self.xws)

    class Meta:
        ordering = ['name']
        unique_together = ('xws', 'faction')


class Pilot(Card, Charges):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE)
    caption = models.CharField(max_length=100, blank=True)
    droid = models.BooleanField(default=False)
    initiative = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(6)]
     )
    actions = models.ManyToManyField(Action, through='PilotAction', through_fields=('pilot', 'action'))

    @property
    def faction(self):
        return self.ship.faction.name


class PilotAction(ActionMixin, models.Model):
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    hard = models.BooleanField(default=False)
    linked_action = models.ForeignKey(Action, related_name='linked_pilot_action',
                                      on_delete=models.CASCADE, null=True, blank=True, default=None)
    linked_hard = models.BooleanField(default=False)


class ShipAction(ActionMixin, models.Model):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    hard = models.BooleanField(default=False)
    linked_action = models.ForeignKey(Action, related_name='linked_ship_action',
                                      on_delete=models.CASCADE, null=True, blank=True, default=None)
    linked_hard = models.BooleanField(default=False)


class Upgrade(Card, Stats, Attacks, Charges):
    slot = models.CharField(max_length=3, choices=UPGRADE_CHOICES)
    slot2 = models.CharField(max_length=3, choices=UPGRADE_CHOICES, null=True, blank=True, default=None)
    ability2 = models.CharField(max_length=320, blank=True, default='')
    ability2_title = models.CharField(max_length=32, blank=True, default='')
    actions = models.ManyToManyField(Action, through='UpgradeAction', through_fields=('upgrade', 'action'))

    def side_actions(self, side):
        return self.upgradeaction_set.filter(side=side)

    @property
    def side_actions_1(self):
        return self.side_actions(1)

    @property
    def side_actions_2(self):
        return self.side_actions(2)

    @property
    def grants(self):
        stats = []
        if self.shields:
            stats.append('+{} [Shield]'.format(self.shields))
        if self.hull:
            stats.append('+{} [Hull]'.format(self.hull))
        if self.agility:
            stats.append('+{} [Agility]'.format(self.agility))
        if self.force:
            stats.append('+{} [Forcecharge]'.format(self.force))
        return '  '.join(stats)

    class Meta:
        ordering = ['slot', 'slot2', 'name']


class UpgradeAction(ActionMixin, models.Model):
    side = models.IntegerField(default=1)
    upgrade = models.ForeignKey(Upgrade, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    hard = models.BooleanField(default=False)
    linked_action = models.ForeignKey(Action, related_name='linked_upgrade_action',
                                      on_delete=models.CASCADE, null=True, blank=True, default=None)
    linked_hard = models.BooleanField(default=False)



##############################
# ### Quick Build models ### #

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
    """
    This model is really the core unit of this app. It takes a pilot+ship, maybe some upgrades, and prepares it for
    presentation.
    """
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
    def action_bar(self):
        pa =  self.pilot.pilotaction_set.all() if self.pilot.pilotaction_set.exists() else self.pilot.ship.shipaction_set.all()
        bar = [p for p in pa]
        upgrades = [card.upgradeaction_set.all() for card in self.upgrades.filter(actions__isnull=False)]
        for card in upgrades:
            for action in card:
                if action not in bar:
                    bar.append(action)
        return bar

    def make_stat(self, stat):
        stat_gt = {'{}__gt'.format(stat): 0}
        return getattr(self.pilot.ship, stat) + sum([getattr(u, stat) for u in self.upgrades.filter(**stat_gt)])

    def make_attack(self, arc):
        arc_gt = {'{}__gt'.format(arc): 0}
        attacks = [getattr(u, arc) for u in self.upgrades.filter(**arc_gt)]
        attacks.append(getattr(self.pilot.ship, arc))
        return max(attacks)

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


    @property
    def front(self): return self.make_attack('front')

    @property
    def left(self): return self.make_attack('left')

    @property
    def right(self):
        return self.make_attack('right')

    @property
    def rear(self):
        return self.make_attack('rear')

    @property
    def turret(self):
        return self.make_attack('turret')

    @property
    def doubleturret(self):
        return self.make_attack('doubleturret')

    @property
    def full_front(self):
        return self.make_attack('full_front')

    @property
    def full_rear(self):
        return self.make_attack('full_rear')

    @property
    def bullseye(self):
        return self.make_attack('bullseye')
