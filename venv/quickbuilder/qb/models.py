from django.db import models

SIZE_CHOICES = (
    ('S', 'Small'),
    ('M', 'Medium'),
    ('L', 'Large')
)

FACTION_CHOICES = (
    ('RA', 'Rebel Alliance'),
    ('GE', 'Galactic Empire'),
    ('SV', 'Scum and Villainy'),
    ('RS', 'Resistance'),
    ('FO', 'First Order'),
    ('GR', 'Galactic Republic'),
    ('SA', 'Seperatist Alliance')
)

UPGRADE_CHOICES = (
    (0, 'Talent'),
    (1, 'Astromech')
)

# base classes

class Card(models.Model):
    name = models.CharField(max_length=64)
    xws = models.CharField(max_length=64, primary_key=True)
    ffg = model.IntegerField

    class Meta:
        abstract = True


# ### components of other cards

class Ability(models.Model):
    title = models.CharField(max_length=32)
    text = models.CharField(max_length=250)


# ### core card models

class Ship(Card):
    size = models.CharField(max_length=1, choices=SIZE_CHOICES, default='S')
    faction = models.CharField(max_length=2, choices=FACTION_CHOICES)


class Pilot(Card):
    ship = models.ForeignKey(Ship,
                             on_delete=models.CASCADE,
                             related_name='pilots',
                             related_query_name='pilot')
    caption = models.CharField(max_length=100)
    initiative = models.IntegerField(choices=(1, 2, 3, 4, 5, 6))
    limited = models.IntegerField(choices=(0, 1, 2, 3), default=0)
    ability = models.CharField(max_length=1000)


class Upgrade(Card):
    limited = models.IntegerField(choices=(0, 1, 2, 3), default=0)


class QuickBuild(models.Model):
    threat = models.IntegerField
    pilot = models.ForeignKey(Pilot,
                              on_delete=models.CASCADE,
                              related_name='quick builds',
                              related_query_name='quick_build')
    upgrades = models.ManyToManyField(Upgrade)