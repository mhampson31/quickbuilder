from django.contrib import admin

from .models import Ship, Pilot, Upgrade, QuickBuild, Faction, Build, Action, ShipAction, UpgradeAction


class BuildInline(admin.TabularInline):
    model = Build
    extra = 0


class ShipActionInline(admin.TabularInline):
    model = ShipAction
    extra = 0


class UpgradeActionInline(admin.TabularInline):
    model = UpgradeAction
    extra = 0


class FactionAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'released')
    list_filter = ('released',)
admin.site.register(Faction, FactionAdmin)


class ShipAdmin(admin.ModelAdmin):
    inlines = (ShipActionInline,)
    list_display = ('display_name', 'faction', 'size')
    list_filter = ('faction', 'size')
admin.site.register(Ship, ShipAdmin)


class UpgradeAdmin(admin.ModelAdmin):
    inlines = (UpgradeActionInline, )
    list_display = ('display_name', 'slot')
    list_filter = ('slot',)
admin.site.register(Upgrade, UpgradeAdmin)


class PilotAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'caption', 'ship', 'faction', 'initiative')
    list_filter = ('ship__faction', 'ship', 'initiative')
admin.site.register(Pilot, PilotAdmin)


class QuickBuildAdmin(admin.ModelAdmin):
    inlines = (BuildInline, )
    list_display = ('pilot_names', 'threat', 'faction')
    list_filter = ('threat', 'faction')
admin.site.register(QuickBuild, QuickBuildAdmin)

admin.site.register(Action)