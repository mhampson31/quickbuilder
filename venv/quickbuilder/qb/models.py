from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


# I'm defining this choice list a little differently, because I need to use the full descs later.
# This keeps them available.


SIZE_TYPES = {
    'Small': 'S',
    'Medium': 'M',
    'Large': 'L'
}


FACTION_TYPES = {
    'Rebel Alliance': 'RA',
    'Galactic Empire': 'GE',
    'Scum and Villainy': 'SV',
    'Resistance': 'RS',
    'First Order': 'FO',
    'Galactic Republic': 'GR',
    'Separatist Alliance': 'SA'
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

FACTION_CHOICES = [(v, k) for k, v in FACTION_TYPES.items()]
SIZE_CHOICES = [(v, k) for k, v in SIZE_TYPES.items()]
UPGRADE_CHOICES = [(v, k) for k, v in UPGRADE_TYPES.items()]

LIMITED_CHOICES = (
    ('1', '•'),
    ('2', '••'),
    ('3', '•••')
)


# base and component classes

class Card(models.Model):
    name = models.CharField(max_length=64)
    xws = models.CharField(max_length=64, primary_key=True)
    ffg = models.PositiveIntegerField(blank=True, null=True, default=None)
    limited = models.CharField(max_length=1, choices=LIMITED_CHOICES, blank=True, default='')
    ability = models.CharField(max_length=320, blank=True, default='')
    ability_title = models.CharField(max_length=32, blank=True, default='')

    @property
    def display_name(self):
        return '{} {}'.format(self.get_limited_display(), self.name).lstrip()

    def __str__(self):
        return self.display_name

    class Meta:
        abstract = True


# ### core models

class Faction(Card):
    limited = None
    ability = None
    cost = None


class Ship(Card):
    size = models.CharField(max_length=1, choices=SIZE_CHOICES, default='S')
    faction = models.CharField(max_length=2, choices=FACTION_CHOICES)
    limited = None
    cost=None

    @property
    def display_name(self):
        return '{} ({})'.format(self.name, self.get_faction_display())


class Pilot(Card):
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE)
    caption = models.CharField(max_length=100)
    initiative = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(6)]
     )


class Upgrade(Card):
    slot = models.CharField(max_length=3, choices=UPGRADE_CHOICES)
    slot2 = models.CharField(max_length=3, choices=UPGRADE_CHOICES, null=True, blank=True, default=None)
    ability2 = models.CharField(max_length=320, blank=True, default='')
    ability2_title = models.CharField(max_length=32, blank=True, default='')


class QuickBuild(models.Model):
    threat = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)]
     )
    faction = models.CharField(max_length=2, choices=FACTION_CHOICES)
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE, related_name='pilot_xws')


    upgrades = models.ManyToManyField(Upgrade, blank=True, related_name='upgrade_xws')

    def __str__(self):
        return '{} ({})'.format(self.pilot.name, self.threat)
