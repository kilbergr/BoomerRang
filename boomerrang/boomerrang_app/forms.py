from django import forms

from boomerrang.boomerrang_app.models import CallRequest


class BoomForm(forms.ModelForm):

    class Meta:
        model = CallRequest
        fields = ('source_num', )
