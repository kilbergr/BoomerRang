# Loads and deletes test data from the database.
# To use: from site root, run `python manage.py manage_data`
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from phonenumber_field.phonenumber import PhoneNumber as ModelPhoneNumber

from boomerrang.boomerrang_app.models import CallRequest, Org, Call, PhoneNumber


class Command(BaseCommand):

    def add_arguments(self, parser):
        # Named optional arguments
        parser.add_argument(
            '--load-db',
            action='store_true',
            default=False,
            dest='load_db',
            help='Load some test data.',
        )

        parser.add_argument(
            '--delete',
            action='store_true',
            default=False,
            dest='delete',
            help='Delete all objects.',
        )

    def handle(self, *args, **options):

        if options['load_db']:
            # Add orgs
            org1 = Org.objects.create(
                    username='OrgCorp',
                    password='truss')
            org2 = Org.objects.create(
                    username='CorpTech',
                    password='truss')

            # Add PhoneNumbers
            number1 = PhoneNumber.objects.create(
                        number=ModelPhoneNumber.from_string(
                            '+15555555555'),
                        validated=None,
                        blacklisted=False)

            # Add CallRequests
            now = timezone.now()
            cr1 = CallRequest.objects.create(
                    source_num=number1,
                    target_num='+15555555555',
                    call_completed=True,
                    time_scheduled=now,
                    org=org1
                    )
            cr2 = CallRequest.objects.create(
                    source_num=number1,
                    target_num='+15555555555',
                    call_completed=True,
                    time_scheduled=now,
                    org=org2
                    )

            # Add Calls
            call1 = Call.objects.create(
                call_time=now,
                success=True,
                duration=40,
                call_request=cr1)
            call2 = Call.objects.create(
                call_time=now,
                success=True,
                duration=45,
                call_request=cr2)

            data = [org1.username, org2.username, number1, cr1, cr2, call1, call2]

            self.stdout.write("Data loaded successfully: {}".format(data))

        elif options['delete']:
            calls = Call.objects.all()
            for c in calls:
                c.delete()
                self.stdout.write('{} deleted'.format(c))

            numbers = PhoneNumber.objects.all()
            for num in numbers:
                num.delete()
                self.stdout.write('{} deleted'.format(num))

            call_requests = CallRequest.objects.all()
            for cr in call_requests:
                cr.delete()
                self.stdout.write('{} deleted'.format(cr))

            orgs = Org.objects.all()
            for o in orgs:
                o.delete()
                self.stdout.write('{} deleted'.format(o))

            if not call_requests and not orgs and not numbers and not calls:
                self.stdout.write("No data to delete.")

        else:
            self.stdout.write('Must pass in either "--load-db" or "--delete"')
            pass
