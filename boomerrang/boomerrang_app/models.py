from django.db import models
from django.core.validators import RegexValidator

from phonenumber_field.modelfields import PhoneNumberField


class Org(models.Model):
    username = models.CharField(max_length=254)
    password = models.CharField(max_length=254)


class CallRequest(models.Model):
    source_num = PhoneNumberField()
    target_num = PhoneNumberField()
    call_completed = models.NullBooleanField()
    time_scheduled = models.DateTimeField(auto_now=False)
    org = models.ForeignKey(Org, models.SET_NULL, blank=True, null=True, related_name="call_requests")


class Call(models.Model):
    call_time = models.DateTimeField(auto_now=False)
    success = models.NullBooleanField()
    duration = models.DateTimeField(auto_now=False, null=True)
    call_request = models.ForeignKey(CallRequest,  models.SET_NULL, blank=True, null=True, related_name="calls")
