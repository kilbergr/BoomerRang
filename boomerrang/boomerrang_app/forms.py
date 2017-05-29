from django import forms

from boomerrang.boomerrang_app.models import CallRequest


class BoomForm(forms.ModelForm):
    time_scheduled = forms.DateTimeField(input_formats=['%m-%d-%Y %H:%M'])

    class Meta:
        model = CallRequest
        fields = ('source_num', 'target_num', 'time_scheduled')

    def __init__(self, *args, **kwargs):
        super(BoomForm, self).__init__(*args, **kwargs)
        self.fields['source_num'].label = "Your number"
        self.fields['target_num'].label = "Call number"
        self.fields['time_scheduled'].label = "When would you like to receive call? "
