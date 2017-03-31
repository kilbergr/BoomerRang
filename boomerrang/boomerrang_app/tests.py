import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Org, CallRequest, Call
from . import views
from . import view_helpers


class ModelTests(TestCase):

	def test_callrequest_has_org(self):
		# Create two org objects
		org = Org(username='boblah', password='blah')
		org2 = Org(username='org2', password='pw2')
		# Create a call_req with one of them
		call_req = CallRequest(
			source_num='+15107571675', target_num='+15107571675', org=org)

		# Expected org should be on call_request obj
		self.assertEqual(call_req.org, org)
		self.assertNotEqual(call_req.org, org2)

	def test_call_must_have_callrequest_to_save(self):
		# Create a call object without a request
		call_time = timezone.now()
		call = Call(call_time=call_time)

		# Raise exception when attempting to save call obj
		with self.assertRaises(Exception):
			call.save()


class ViewTests(TestCase):

    def test_index_response(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

   # TODO: (Rebecca) Needs views tests that test Twilio
   #  def test_create_call(self):
   #  	test_num, test_sid, test_token = view_helpers.load_twilio_config()
   #  	self.client.calls.create(url="http://demo.twilio.com/docs/voice.xml",
			# to="+14108675309",
			# from_="+15005550006")
   #  	self.assertEqual(CallStatus.Success, client.call.Status);

   #  	response = self.client.post('/', {'form': {'source_num': '+19175263426'}})


class ViewHelpersTests(TestCase):

    def test_load_twilio_config(self):
    	test_num, test_sid, test_token = view_helpers.load_twilio_config()
    	self.assertEqual(len(test_token), 32)
    	self.assertEqual(len(test_sid), 34)
    	self.assertIn('+1', test_num)
