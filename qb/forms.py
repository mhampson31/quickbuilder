from django import forms
from .models import Faction

class RandomListForm(forms.Form):
    faction = forms.ModelChoiceField(label="Faction", queryset=Faction.objects.all(), to_field_name='id')
    threat = forms.IntegerField(label='Threat', initial=8)
