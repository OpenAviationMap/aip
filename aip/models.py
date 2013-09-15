from django.contrib.gis.db import models

class Feature(models.Model):
    name = models.CharField(max_length=50)
    objects = models.GeoManager()

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

class Icao(models.Model):
    icao = models.CharField(max_length=4)
    objects = models.GeoManager()

    class Meta:
        abstract = True

class Country(Feature):
    geometry = models.MultiPolygonField()

class Airspace(Feature):
    country = models.OneToOneField(Country)
    geometry = models.MultiPolygonField()

class Aerodrome(Feature, Icao):
    point = models.PointField()

class Runway(Feature):
    surface = models.CharField(max_length=24)
    directions = models.CharField(max_length=7)
    geometry = models.LineStringField()
    aerodrome = models.ForeignKey(Aerodrome)

class Navaid(Feature):
    country = models.OneToOneField(Country)
    point = models.PointField()
