from django.db import models
from django.core.validators import RegexValidator


class Org(models.Model):
    username = models.CharField(max_length=254)
    password = models.CharField(max_length=254)

class CallRequest(models.Model):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{8,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    source_num = models.CharField(validators=[phone_regex], max_length=16)
    target_num = models.CharField(validators=[phone_regex], max_length=16)
    call_completed = models.NullBooleanField(null=True)
    time_scheduled = models.DateTimeField(auto_now=False)
    org = models.ForeignKey(Org, related_name="call_requests")

class Call(models.Model):
    call_time = models.DateTimeField(auto_now=False)
    success = models.NullBooleanField(null=True)
    duration = models.DateTimeField(auto_now=False, null=True)
    call_request = models.ForeignKey(CallRequest, related_name="calls")
