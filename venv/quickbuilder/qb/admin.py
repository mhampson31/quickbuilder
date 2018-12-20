from django.contrib import admin

from .models import Ship, Pilot, Upgrade, QuickBuild, Faction, Build

for m in Ship, Pilot, Upgrade, Faction:
    admin.site.register(m)

class BuildInline(admin.TabularInline):
    model = Build
    extra = 0

class QuickBuildAdmin(admin.ModelAdmin):
    inlines = (BuildInline, )
    list_display = ('pilot_names', 'threat', 'faction')
    list_filter = ('threat', 'faction')

admin.site.register(QuickBuild, QuickBuildAdmin)
