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
    cost=None

    class Meta:
        ordering = ['name']
        unique_together = ('xws', 'faction')


class Pilot(Card):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE)
    caption = models.CharField(max_length=100)
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


class QuickBuild(models.Model):
    threat = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)]
     )
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    pilots = models.ManyToManyField(Pilot,
                                    through='Build',
                                    through_fields=('quickbuild', 'pilot'),
                                    related_name='pilot_xws')

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
    pilot = models.ForeignKey(Pilot, related_name='qb_pilot_xws', on_delete=models.CASCADE)
    upgrades = models.ManyToManyField(Upgrade, blank=True, related_name='upgrade_xws')

    def __str__(self):
        return self.pilot.name

    @property
    def limited_names(self):
        # QuickBuilds and Builds have a similar property, used to collect any limited pilots/upgrades in use
        lnames = make_lnames()
        cards = [u for u in self.upgrades.all() if u.limited != '0']
        if self.pilot.limited != '0':
            cards.append(self.pilot)

        for c in cards:
            lnames[c.limited].append(c.name)

        return lnames