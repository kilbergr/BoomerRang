from django import forms

from boomerrang.boomerrang_app.models import CallRequest


class BoomForm(forms.ModelForm):
    time_scheduled = forms.DateTimeField(input_formats=['%m-%d-%Y'])

    class Meta:
        model = CallRequest
        fields = ('source_num', 'target_num', 'time_scheduled')
