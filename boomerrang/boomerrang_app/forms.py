from django import forms

from phonenumber_field.formfields import PhoneNumberField

from boomerrang.boomerrang_app.models import CallRequest


class BoomForm(forms.Form):
    source_num = PhoneNumberField()
    target_num = PhoneNumberField()
    time_scheduled = forms.DateTimeField(input_formats=['%m-%d-%Y %H:%M'])

    def __init__(self, *args, **kwargs):
        super(BoomForm, self).__init__(*args, **kwargs)
        self.fields['source_num'].label = "Your number"
        self.fields['target_num'].label = "Call number"
        self.fields['time_scheduled'].label = "When would you like to receive call? "
