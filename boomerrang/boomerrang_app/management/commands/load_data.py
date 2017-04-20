# Loads and deletes test data from the database.
# To use: from site root, run `python manage.py load_data`
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from boomerrang.boomerrang_app.models import CallRequest, Org, Call

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
            org1.save()
            org2.save()

            # Add CallRequests
            now = timezone.now()
            cr1 = CallRequest.objects.create(
                    source_num='19175263426',
                    target_num='15102894755',
                    time_scheduled=now,
                    org=org1
                    )
            cr2 = CallRequest.objects.create(
                    source_num='15102894755',
                    target_num='19175263426',
                    time_scheduled=now,
                    org=org2
                    )
            cr1.save()
            cr2.save()

            data = [org1.username, org2.username, cr1, cr2]

            self.stdout.write("Data loaded successfully: {}".format(data))

        elif options['delete']:
            call_requests = CallRequest.objects.all()
            for cr in call_requests:
                cr.delete()
                self.stdout.write('{} deleted'.format(cr))

            orgs = Org.objects.all()
            for o in orgs:
                o.delete()
                self.stdout.write('{} deleted'.format(o))

            calls = Call.objects.all()
            for c in calls:
                c.delete()
                self.stdout.write('{} deleted'.format(c))

            if not call_requests and not orgs and not calls:
                self.stdout.write("No data to delete.")

        else:
            self.stdout.write('Must pass in either "--load-db" or "--delete"')
            pass
