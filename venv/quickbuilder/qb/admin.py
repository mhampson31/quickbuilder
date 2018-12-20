from django.contrib import admin

from .models import Ship, Pilot, Upgrade, QuickBuild, Faction


admin.site.register(Ship)
admin.site.register(Pilot)
admin.site.register(Upgrade)
admin.site.register(QuickBuild)
admin.site.register(Faction)