# encoding: UTF-8

from django.db import models
from django.utils.safestring import mark_safe

from qb.templatetags.qb_extras import get_icon
from .choices import LIMITED_CHOICES, ARC_CHOICES, RANGE_CHOICES


def make_lnames():
    """
    this is a utility function to help compare the names of limited cards across a build
    :return: a dictionary in the form of {n:[], ...} where n is each possible count of limited pips on a card.
    The idea is that if a card has, say, one limited pip, we append its name to the list under that key, and can
    count the number of times it occurs there later.
    There's probably a more efficient/clever way to do this but it works for now.
    """
    lnames = {}
    for k, v in LIMITED_CHOICES:
        lnames[k] = []
    return lnames


class Card(models.Model):
    name = models.CharField(max_length=64)
    xws = models.CharField(max_length=64, db_index=True)
    ffg = models.PositiveIntegerField(blank=True, null=True, default=None)
    limited = models.CharField(max_length=1, choices=LIMITED_CHOICES, blank=True, default='')
    ability = models.CharField(max_length=400, blank=True, default='')
    condition = models.OneToOneField('Condition', on_delete=models.CASCADE, blank=True, null=True, default=None)

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


class Attack(models.Model):
    arc = models.CharField(max_length=2, choices=ARC_CHOICES, default='FT')
    value = models.PositiveIntegerField(default=2)
    range = models.CharField(max_length=2, choices=RANGE_CHOICES, default='13')
    ordanance = models.BooleanField(default=False)
    primary = True

    def __str__(self):
        return '{} {}'.format(self.get_arc_display(), self.value)

    @property
    def display_name(self):
        return mark_safe('<span class="attack">[{}]</span> {}{}{}'.format(self.get_arc_display(),
                                     self.value,
                                     ' {} '.format(get_icon('rangebonusindicator', css='attack')) if self.ordanance else '',
                                     ' Range {}'.format(self.get_range_display()) if self.type is 'special' else ''))

    class Meta:
        abstract = True


class Condition(models.Model):
    name = models.CharField(max_length=64)
    effect = models.CharField(max_length=300)
    xws = models.CharField(max_length=64, db_index=True)

    def __str__(self):
        return self.name


class Stats(models.Model):
    agility = models.PositiveIntegerField(default=0)
    shields = models.PositiveIntegerField(default=0)
    hull = models.PositiveIntegerField(default=0)

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
            name = '<span class="icon">{}{}{}</span>'.format(get_icon(self.action.icon, css='hard' if self.hard else None),
                                     get_icon('linked', css='linked'),
                                     get_icon(self.linked_action.icon, css='hard' if self.linked_hard else None))
        else:
            name = '<span class="icon">{}</span>'.format(get_icon(self.action.icon, css='hard' if self.hard else None))
        return mark_safe(name)


# ### core models

class Faction(models.Model):
    name = models.CharField(max_length=64)
    xws = models.CharField(max_length=64, db_index=True)
    ffg = models.PositiveIntegerField(blank=True, null=True, default=None)
    released = models.BooleanField(default=True)

    def __str__(self):
        return self.name
