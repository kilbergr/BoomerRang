from django.db import models
from django.core.validators import RegexValidator
import logging

from phonenumber_field.modelfields import PhoneNumberField

log = logging.getLogger('boom_logger')

class Org(models.Model):
    username = models.CharField(max_length=254)
    password = models.CharField(max_length=254)


class CallRequest(models.Model):
    source_num = PhoneNumberField()
    target_num = PhoneNumberField()
    call_completed = models.NullBooleanField()
    time_scheduled = models.DateTimeField(auto_now=False)
    org = models.ForeignKey(Org, related_name="call_requests")

    class Meta:
        unique_together = ('source_num',
                           'target_num',
                           'time_scheduled',
                           'call_completed',
                           'org')


class Call(models.Model):
    call_time = models.DateTimeField(auto_now=False)
    success = models.NullBooleanField()
    duration = models.DateTimeField(auto_now=False, null=True)
    call_request = models.ForeignKey(CallRequest, related_name="calls")
