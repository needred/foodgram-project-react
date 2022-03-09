from django import forms

from .models import Tag
from .widgets import ColorPicker


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        widgets = {
            'color': ColorPicker,
        }
        fields = '__all__'
