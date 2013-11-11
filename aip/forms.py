from models import Airspace, Country
from django import forms
from django.forms import ModelForm

class OsmXmlForm(forms.Form):
    country = forms.ModelChoiceField(Country.objects)
    osm_xml = forms.FileField()

class AirspaceForm(ModelForm):
    geometry = forms.CharField()
    class Meta:
        model = Airspace

class MultiPolygonField(forms.CharField):
    def clean(self, value):
        value = super(self,forms.CharField).clean(self, value)

class BatchDataForm(forms.Form):
    data = forms.CharField(widget=forms.Textarea)
    data_type = forms.CharField()
