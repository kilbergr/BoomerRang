from django import forms

from boomerrang_app.models import CallRequest


class BoomForm(forms.ModelForm):

    class Meta:
        model = CallRequest
        fields = ('source_num', 'target_num', 'time_scheduled', 'org')
