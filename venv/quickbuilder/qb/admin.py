from django.contrib import admin

from .models import Ability, Ship, Pilot, Upgrade, QuickBuild, Faction

class ShipAdmin(admin.ModelAdmin):
    exclude = ('ability_text', 'ability_title')
admin.site.register(Ship, ShipAdmin)

admin.site.register(Pilot)
admin.site.register(Upgrade)
admin.site.register(QuickBuild)
admin.site.register(Ability)
admin.site.register(Faction)