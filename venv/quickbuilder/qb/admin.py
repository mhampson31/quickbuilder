from django.contrib import admin

from .models import Ship, Pilot, Upgrade, QuickBuild, Faction, Build, Action, PilotAction, ShipAction, UpgradeAction

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


class PilotActionInline(admin.TabularInline):
    model = PilotAction
    extra = 0


class UpgradeActionInline(admin.TabularInline):
    model = UpgradeAction
    extra = 0


class FactionAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'released')
    list_filter = ('released',)
admin.site.register(Faction, FactionAdmin)


class ShipAdmin(admin.ModelAdmin):
    inlines = (ShipActionInline, )
    fieldsets = (
            (None, {'fields':('name', 'faction', 'size')}),
            ('Primary Weapons', {'fields': (('front', 'turret', 'doubleturret'),)}),
             ('Defenses', {'fields': (('agility', 'shields', 'hull'),)}),
             ('Powers', {'fields': (('force', 'charge', 'charge_regen'),)}),
             ('Primary (Uncommon)', {'fields': (('left', 'right', 'rear', 'bullseye', 'full_front', 'full_rear'),)})
          )
    list_filter = ('faction', 'size')
admin.site.register(Ship, ShipAdmin)


class UpgradeAdmin(admin.ModelAdmin):
    inlines = (UpgradeActionInline, )
    fieldsets = (
        (None, {'fields': (('name', 'limited'), 'xws', 'ability', ('slot', 'slot2'))}),
        ('Primary Weapons', {'fields': (('front', 'turret', 'doubleturret'),)}),
        ('Defenses', {'fields': (('agility', 'shields', 'hull'),)}),
        ('Powers', {'fields': (('force', 'charge', 'charge_regen'),)}),
        ('Primary (Uncommon)', {'fields': (('left', 'right', 'rear', 'bullseye', 'full_front', 'full_rear'),)})
    )
    list_display = ('display_name', 'slot')
    list_filter = ('slot',)
admin.site.register(Upgrade, UpgradeAdmin)


class PilotAdmin(admin.ModelAdmin):
    inlines = (PilotActionInline,)
    fieldsets = (
        (None, {'fields':(('name', 'initiative'), 'caption', 'ship', 'ability')}),
         ('Primary Weapons', {'fields': (('front', 'turret', 'doubleturret'),)}),
        ('Defenses', {'fields': (('agility', 'shields', 'hull'),)}),
        ('Powers', {'fields': (('force', 'charge', 'charge_regen'),)}),
       ('Primary (Uncommon)', {'fields': (('left', 'right', 'rear', 'bullseye', 'full_front', 'full_rear'),)})
    )
    list_display = ('display_name', 'caption', 'faction', 'ship', 'initiative')
    list_filter = ('ship__faction', 'ship', 'initiative')
admin.site.register(Pilot, PilotAdmin)


class QuickBuildAdmin(admin.ModelAdmin):
    inlines = (BuildInline, )
    list_display = ('pilot_names', 'threat', 'faction')
    list_filter = ('threat', 'faction')
admin.site.register(QuickBuild, QuickBuildAdmin)

admin.site.register(Action)