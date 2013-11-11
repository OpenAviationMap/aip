from forms import AirspaceForm, BatchDataForm, OsmXmlForm
from models import Aerodrome, Airspace, Navaid, Country, Height, Frequency
from django.contrib.gis.geos import Point, MultiPolygon
from django.shortcuts import render_to_response, render
from lxml import etree
from django.contrib.gis.geos import GEOSGeometry
from django.db import transaction
from pyparsing import *

import re

import csv # to parse CSV files

def get_navaid_frequencies(ts):
    freqs = []
    freqTypes = ['dme','vor','ndb','ils','tacan']

    errs = []

    for t in freqTypes:
        if 'navaid:%s' % t in ts:
            try:
                f = Frequency()
                f.freq = ts['navaid:%s' % t]
                f.use = t
                freqs.append(f)
            except Exception,e:
                errs.append(str(e)+' STR: "%s"' % ts['navaid:%s' % t])
    if len(freqs) == 0:
        errs.append('Navaid has no frequencies')
    return (freqs,errs)

def get_height(ts):
    errs = []
    if 'height' not in ts:
        errs.append('height missing')
    if 'height:unit' not in ts:
        errs.append('height:unit missing')
    if 'height:class' not in ts and ts.get('height:unit','').lower()=='fl':
        errs.append('height:class required for all heights except flight levels')
    if len(errs)==0:
        h = Height()
        h.num = int(round(float(ts['height'])))
        h.unit = ts['height:unit'].lower()
        if h.unit is not 'fl':
            h.reference = ts['height:class'].lower()
        return (h,[])
    else:
        return (None,errs)

def nodeClassifier(lat, lon, ts, linenumber, country):
    if ts.get('navaid')=='yes':
        return NavaidObj(lat, lon, ts, linenumber, country)
    elif ts.get('aerodrome')=='yes':
        return AerodromeObj(lat, lon, ts, linenumber, country)
    else:
        return None

class NodeObj(object):
    def __init__(self, lat, lon, tags, linenumber, country):
        self.lat = lat
        self.lon = lon
        self.tags = tags
        self.linenumber = linenumber
        self.country = country

    def validate(self):
        errs = []
        if abs(self.lat) > 180:
            errs.append('Latitude can not be greater than 180 degrees, l%i' % self.linenumber)
        if abs(self.lon) > 90:
            errs.append('Longditude can not be greater than 90 degrees, l%i' % self.linenumber)
        return errs

class AerodromeObj(NodeObj):
    def validate(self):
        errs = super(AerodromeObj, self).validate()
        if 'name' not in self.tags:
            errs.append('Aerodromes require a name l%i' % self.linenumber)

        (height, herrs) = get_height(self.tags)
        if len(herrs)==0:
            self.elevation = height
        else:
            for e in herrs:
                errs.append(e + ' l%i' % self.linenumber)
        return errs

    def save(self):
        if len(self.validate())==0:
            a = Aerodrome()
            a.name = self.tags.get('name')
            a.point = Point(self.lon, self.lat, srid=4326)
            a.country = self.country
            self.elevation.save()
            a.elevation = self.elevation
            a.save()

class NavaidObj(NodeObj):
    def validate(self):
        errs = super(NavaidObj, self).validate()
        if 'name' not in self.tags:
            errs.append('Navaids require a name l%i' % self.linenumber)
        (freqs, ferrs) = get_navaid_frequencies(self.tags)
        if len(ferrs) == 0:
            self.freqs = freqs
        else:
            for e in ferrs:
                errs.append(e + ' l%i' % self.linenumber)
        return errs

    def save(self):
        if len(self.validate())==0:
            n = Navaid()
            n.name = self.tags.get('name')
            n.point = Point(self.lon, self.lat, srid=4326)
            n.country = self.country
            n.save()
            n.frequency_set = self.freqs
            map(lambda f: f.save(), self.freqs)

@transaction.atomic
def import_osm_xml(request):
    if request.POST:
        osm_xml_form = OsmXmlForm(request.POST, request.FILES)
        if osm_xml_form.is_valid():
            root = etree.parse(request.FILES['osm_xml'])

            # get all the nodes of the document
            nodes = {}
            for n in root.iter('node'):
                tags = {}
                for t in n.iter('tag'):
                    tags[t.get('k')] = t.get('v')
                nodes[int(n.get('id'))] = (float(n.get('lat')), float(n.get('lon')), tags, n.sourceline)

            # create a list of all the ways in the dacuments
            ways = {}
            for w in root.iter('way'):
                tags = {}
                for t in w.iter('tag'):
                    tags[t.get('k')] = t.get('v')

                line_string = []
                for nid in w.iter('nd'):
                    lat = nodes[int(nid.get('ref'))][0]
                    lon = nodes[int(nid.get('ref'))][1]
                    line_string.append((lat, lon))
                ways[int(w.get('id'))] = (line_string, tags)

            errs = []
            country = Country.objects.get(code=request.POST['country'])
            for n in nodes.itervalues():
                nobj = nodeClassifier(n[0], n[1], n[2], n[3], country)
                if nobj:
                    errs += nobj.validate()
                    nobj.save()
        else:
            return render(request, 'aip/form.html', {'form':osm_xml_form})
    osm_xml_form = OsmXmlForm()
    return render(request, 'aip/form.html', {'form':osm_xml_form})

def import_airspaces(request):
    if request.POST:
        airspace_form = AirspaceForm(request.POST)
        if airspace_form.is_valid():
            space = parse_coord_list(airspace_form.data)
    airspace_form = AirspaceForm()
    return render_template()

def parse_coord_list(text):
    ret = []
    for line in split('\n'):
        for [lat, lon] in line.strip().split(' '):
            ret.append( (float(lat.strip()), float(lon.strip())) )
    return ret
