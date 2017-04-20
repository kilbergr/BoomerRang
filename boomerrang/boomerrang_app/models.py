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
    org = models.ForeignKey(Org, on_delete=models.SET_NULL, null=True, related_name="call_requests")

    def save(self, *args, **kwargs):
        if not self.org:
            log.warning("CallRequest object must have an org to be entered into db.")
            return
        else:
            super(CallRequest, self).save(*args, **kwargs)


class Call(models.Model):
    call_time = models.DateTimeField(auto_now=False)
    success = models.NullBooleanField()
    duration = models.DateTimeField(auto_now=False, null=True)
    call_request = models.ForeignKey(CallRequest, on_delete=models.SET_NULL, null=True, related_name="calls")

    def save(self, *args, **kwargs):
        if not self.call_request:
            log.warning("Call object must have a CallRequest object to be entered into db.")
            return
        else:
            super(Call, self).save(*args, **kwargs)

