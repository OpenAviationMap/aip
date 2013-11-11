from django.contrib.gis.db import models

class Feature(models.Model):
    name = models.CharField(max_length=124)
    remarks = models.CharField(max_length=255)
    objects = models.GeoManager()

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

    @classmethod
    def lookup(cls, obj):
        if obj.get('id',False):
            cls.objects.get

class Icao(models.Model):
    icao = models.CharField(max_length=4)
    objects = models.GeoManager()

    class Meta:
        abstract = True

height_refs = (
        ('agl', 'AGL'),
        ('amsl', 'AMSL'),
)

height_units = (
        ('ft', 'feet'),
        ('m', 'metres'),
        ('fl', 'flight level'),
)

class Height(models.Model):
    num = models.PositiveIntegerField()
    reference = models.CharField(max_length=4, choices=height_refs, null=True)
    unit = models.CharField(max_length=2, choices=height_units)

    def __unicode__(self):
        if self.unit=='fl':
            return "FL %d" % (self.num,)
        else:
            return "%d%s %s" % (self.num, self.unit.upper(), self.reference.upper())

class Country(Feature):
    geometry = models.MultiPolygonField()
    # ISO3166-1 alpha-2 codes http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    code = models.CharField(max_length=2, primary_key=True)

class Airspace(Feature):
    country = models.ForeignKey(Country)
    geometry = models.MultiPolygonField()
    lower = models.ForeignKey(Height, related_name='airspace_lower', verbose_name='airspace lower height')
    upper = models.ForeignKey(Height, related_name='airspace_upper', verbose_name='airspace upper height')

class Aerodrome(Feature, Icao):
    point = models.PointField()
    country = models.ForeignKey(Country)
    elevation = models.ForeignKey(Height)

class Runway(Feature):
    surface = models.CharField(max_length=32)
    directions = models.CharField(max_length=8)
    geometry = models.LineStringField()
    aerodrome = models.ForeignKey(Aerodrome)
    elevation = models.ForeignKey(Height)

class Navaid(Feature):
    country = models.ForeignKey(Country)
    identifier = models.CharField(max_length=32)
    point = models.PointField()

class Frequency(models.Model):
    use = models.CharField(max_length=10)
    freq = models.CharField(max_length=32)
    navaid = models.ForeignKey(Navaid)

