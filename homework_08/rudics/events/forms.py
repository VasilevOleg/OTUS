from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "date",
            "csq",
            "sv",
            "beam",
            "start",
            "finish",
            "bytes",
            "duration",
            "speed",
        ]
