from forms import AirspaceForm, BatchDataForm
from models import Aerodrome, Airspace, Navaid
from django.contrib.gis.geos import Point, MultiPolygon
from django.shortcuts import render_to_response, render

import csv # to parse CSV files

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

def batch_insert_point(request):
    if request.POST:
        f = BatchDataForm(request.POST)
        if f.is_valid():
            objects = f.cleaned_data['data']
            t = f.cleaned_data['data_type']
            if t == 'Aerodrome':
                for aerodrome in objects.split('\n'):
                    aerodrome = aerodrome.split(',')
                    a = Aerodrome()
                    a.point = Point(float(aerodrome[0]), float(aerodrome[1]))
                    a.name = aerodrome[2]
                    a.icao = aerodrome[3]
                    a.save()
                return HttpResponse(content='success')
            elif t == 'Navaid':
                for navaid in objects.split('\n'):
                    navaid = navaid.split(',')
                    n = Navaid()
                    n.point = Point(float(navaid[0]), float(navaid[1]))
                    n.name = navaid[2]
                    n.save()
                return HttpResponse(content='success, request')
    f = BatchDataForm()
    return render(request, 'aip/form.html', {'form':f})
