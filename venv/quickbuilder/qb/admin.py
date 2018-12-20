from django.contrib import admin

from .models import Ship, Pilot, Upgrade, QuickBuild, Faction, Build

for m in Ship, Faction:
    admin.site.register(m)


class UpgradeAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'slot')
    list_filter = ('slot',)
admin.site.register(Upgrade, UpgradeAdmin)


class PilotAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'caption', 'ship', 'faction', 'initiative')
    list_filter = ('ship', 'initiative')
admin.site.register(Pilot, PilotAdmin)


class BuildInline(admin.TabularInline):
    model = Build
    extra = 0


class QuickBuildAdmin(admin.ModelAdmin):
    inlines = (BuildInline, )
    list_display = ('pilot_names', 'threat', 'faction')
    list_filter = ('threat', 'faction')
admin.site.register(QuickBuild, QuickBuildAdmin)
