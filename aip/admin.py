from django.contrib.gis import admin
from models import Country, Airspace, Aerodrome, Navaid, Runway

admin.site.register(Country, admin.GeoModelAdmin)
admin.site.register(Airspace, admin.GeoModelAdmin)
admin.site.register(Aerodrome, admin.GeoModelAdmin)
admin.site.register(Navaid, admin.GeoModelAdmin)
admin.site.register(Runway, admin.GeoModelAdmin)
