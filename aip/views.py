# Create your views here.
from forms import AirspaceForm
from models import Airspace
from django.contrib.gis.geos import MultiPolygon

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
