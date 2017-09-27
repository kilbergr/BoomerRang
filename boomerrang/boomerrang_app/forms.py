from bootstrap3_datetime.widgets import DateTimePicker
from django import forms
from phonenumber_field.formfields import PhoneNumberField
from timezone_field import TimeZoneFormField


class BoomForm(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'
    source_num = PhoneNumberField()
    target_num = PhoneNumberField()
    time_scheduled = forms.DateTimeField(
        input_formats=['%Y-%m-%d %H:%M'],
        widget=DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                       "sideBySide": True,
                                       "minDate": "moment",
                                       # 5 minute increments
                                       "stepping": 5}))
    timezone = TimeZoneFormField()
    time_scheduled_utc = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M:%S.%fZ'],
        widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(BoomForm, self).__init__(*args, **kwargs)
        self.fields['source_num'].label = "Your number"
        self.fields['source_num'].widget.attrs['placeholder'] = "e.g. +15555555555"
        self.fields['target_num'].label = "Call number (Pre-programmed)"
        # TODO (rebecca): Remove below to allow editing once out of user research
        self.fields['target_num'].widget.attrs['readonly'] = "readonly"
        self.fields[
            'time_scheduled'].label = "When would you like to receive call? "
