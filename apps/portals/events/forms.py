from django import forms
from apps.events.models import Event


class AddEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields=('name','is_visible','short_description','event_type','category','has_tdp','team_size_min','team_size_max','registration_starts','registration_ends','google_group','email','coords',)
