from django.contrib import admin

from .models import Ship, Pilot, Upgrade, QuickBuild, Faction, Build, Action,\
    ShipAction, UpgradeAction, UpgradeAttack, ShipAttack

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
    list_display = ('display_name', 'released')
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
        (None, {'fields': (('name', 'limited'), 'xws', 'ability', ('slot', 'slot2'))}),
        ('Powers', {'fields': (('charge', 'charge_regen', 'force'),)}),
        ('Defenses', {'fields': (('agility', 'shields', 'hull'),)}),
        )
    list_display = ('display_name', 'slot', 'charge', 'ability')
    list_filter = ('slot',)
admin.site.register(Upgrade, UpgradeAdmin)


class PilotAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields':(('name', 'initiative'), 'caption', 'ship', 'ability', 'droid')}),
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

admin.site.register(Action)
