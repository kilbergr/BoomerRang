# -*- coding: utf-8 -*-

import django
from django.core.management import call_command

from boomerrang.boomerrang_app.models import CallRequest, Org, Call, PhoneNumber


class LoadDataTests(django.test.TestCase):
	def test_load_data(self):
		# Given: an empty database
		self.assertEqual(len(Call.objects.all()), 0)
		self.assertEqual(len(Org.objects.all()), 0)
		self.assertEqual(len(PhoneNumber.objects.all()), 0)
		self.assertEqual(len(CallRequest.objects.all()), 0)

		# When: manage_data --load-db is called
		call_command('manage_data', '--load-db')

		# Then: Expected number of instances are created.
		self.assertEqual(len(Call.objects.all()), 2)
		self.assertEqual(len(Org.objects.all()), 2)
		self.assertEqual(len(PhoneNumber.objects.all()), 1)
		self.assertEqual(len(CallRequest.objects.all()), 2)

	def test_delete_data(self):
		# Given: some object instances in the database
		call_command('manage_data', '--load-db')
		self.assertEqual(len(Call.objects.all()), 2)
		self.assertEqual(len(Org.objects.all()), 2)
		self.assertEqual(len(PhoneNumber.objects.all()), 1)
		self.assertEqual(len(CallRequest.objects.all()), 2)

		# When: manage_data --delete-db is called
		call_command('manage_data', '--delete')

		# Then: Database is now empty
		self.assertEqual(len(Call.objects.all()), 0)
		self.assertEqual(len(Org.objects.all()), 0)
		self.assertEqual(len(PhoneNumber.objects.all()), 0)
		self.assertEqual(len(CallRequest.objects.all()), 0)

	def test_delete_data_empty_db(self):
		# Given: an empty database
		self.assertEqual(len(Call.objects.all()), 0)
		self.assertEqual(len(Org.objects.all()), 0)
		self.assertEqual(len(PhoneNumber.objects.all()), 0)
		self.assertEqual(len(CallRequest.objects.all()), 0)

		# When: manage_data --delete-db is called
		call_command('manage_data', '--delete')

		# Then: database remains empty
		self.assertEqual(len(Call.objects.all()), 0)
		self.assertEqual(len(Org.objects.all()), 0)
		self.assertEqual(len(PhoneNumber.objects.all()), 0)
		self.assertEqual(len(CallRequest.objects.all()), 0)
