from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Ship, Pilot, Upgrade, QuickBuild, Faction, Build, Action,\
    ShipAction, UpgradeAction, UpgradeAttack, ShipAttack, Condition, Collection

stat_fields = (
    (None, {'fields':('name', 'caption', 'initiative')}),
    ('Primary Weapons', {'fields': (('front', 'turret', 'doubleturret'),)}),
    ('Defenses', {'fields': (('agility', 'shields', 'hull'),)}),
    ('Powers', {'fields': (('force', 'charge', 'charge_regen'),)}),
    ('Primary (Uncommon)', {'fields': (('left', 'right', 'rear', 'bullseye', 'full_front', 'full_rear'),)})
)


class BuildInline(admin.TabularInline):
    model = Build
    extra = 0


class ShipActionInline(admin.TabularInline):
    model = ShipAction
    extra = 0


class ShipAttackInline(admin.TabularInline):
    model = ShipAttack
    extra = 0


class UpgradeAttackInline(admin.TabularInline):
    model = UpgradeAttack
    extra = 0


class UpgradeActionInline(admin.TabularInline):
    model = UpgradeAction
    extra = 0


class FactionAdmin(admin.ModelAdmin):
    list_display = ('name', 'released')
    list_filter = ('released',)
admin.site.register(Faction, FactionAdmin)


class ShipAdmin(admin.ModelAdmin):
    inlines = (ShipAttackInline, ShipActionInline)
    fieldsets = (
            (None, {'fields':('name', 'faction', 'size')}),
            ('Defenses', {'fields': (('agility', 'shields', 'hull'),)}),
          )
    list_filter = ('faction', 'size')
    list_display = ('name', 'faction', 'size')
admin.site.register(Ship, ShipAdmin)


class UpgradeAdmin(admin.ModelAdmin):
    inlines = (UpgradeAttackInline, UpgradeActionInline, )
    fieldsets = (
        (None, {'fields': (('name', 'limited'),
                           ('slot', 'slot2'),
                           'xws',
                           'ability',
                           'condition',
                           'side2'
                           )}),
        ('Powers', {'fields': (('charge', 'charge_regen', 'force'),)}),
        ('Defenses', {'fields': (('agility', 'shields', 'hull'),)}),
        )
    list_display = ('display_name', 'slot', 'charge', 'ability')
    list_filter = ('slot',)
admin.site.register(Upgrade, UpgradeAdmin)


class PilotAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields':(('name', 'initiative'),
                          'caption',
                          'ship',
                          'droid',
                          'ability',
                          'condition'
                          )}),
        ('Powers', {'fields': (('force', 'charge', 'charge_regen'),)}),
        )
    list_display = ('display_name', 'caption', 'faction', 'ship', 'initiative', 'droid')
    list_filter = ('ship__faction', 'ship', 'initiative', 'droid')
admin.site.register(Pilot, PilotAdmin)


class QuickBuildAdmin(admin.ModelAdmin):
    inlines = (BuildInline, )
    list_display = ('pilot_names', 'threat', 'faction')
    list_filter = ('threat', 'faction')
admin.site.register(QuickBuild, QuickBuildAdmin)


class CollectionInline(admin.StackedInline):
    model = Collection
    can_delete = False
    verbose_name_plural = 'collection'


class UserAdmin(BaseUserAdmin):
    inlines = (CollectionInline, )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


admin.site.register(Action)
admin.site.register(Condition)