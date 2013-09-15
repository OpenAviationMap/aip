from models import Airspace
from django import forms
from django.forms import ModelForm

class AirspaceForm(ModelForm)
    geometry = forms.CharField()
    class Meta:
        model = Airspace

class MultiPolygonField(forms.CharField):
    def clean(self, value):
        value = super(self,forms.CharField).clean(self, value)
