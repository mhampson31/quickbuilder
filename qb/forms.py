from django import forms
from .models import Faction

class RandomListForm(forms.Form):
    faction = forms.ModelChoiceField(label="Faction",
                                     queryset=Faction.objects.filter(released=True),
                                     to_field_name='id',
                                     empty_label='')
    threat = forms.IntegerField(label='Threat', initial=8)
