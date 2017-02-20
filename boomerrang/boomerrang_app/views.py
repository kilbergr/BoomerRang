from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponse
from django.shortcuts import render

from twilio import twiml
from twilio.rest import Client
import os

from boomerrang.boomerrang_app.forms import BoomForm
# from boomerrang.boomerrang_app.models import CallRequest, Org, Call


def load_twilio_config():
    twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_number = os.environ.get('TWILIO_NUMBER')

    if not all([twilio_account_sid, twilio_auth_token, twilio_number]):
        print('Twilio auth info not configured.')
        raise MiddlewareNotUsed
    import ipdb; ipdb.set_trace()
    return (twilio_number, twilio_account_sid, twilio_auth_token)


def index(request):
    form = BoomForm()
    return render(request, 'form_test.html', {'form': form})


# Voice Request URL
def call(request):
    (twilio_number, twilio_account_sid, twilio_auth_token) = load_twilio_config()
    import ipdb; ipdb.set_trace()
    if request.method == 'POST':
        import pdb; pdb.set_trace()
        # Get phone number we need to call
        phone_number = request.form.get('phoneNumber', None)
        import ipdb; ipdb.set_trace()

        try:
            twilio_client = Client(twilio_account_sid, twilio_auth_token)
        except Exception as e:
            msg = 'Missing configuration variable: {0}'.format(e)
            return jsonify({'error': msg})

        try:
            import ipdb; ipdb.set_trace()
            twilio_client.calls.create(from_=twilio_number,
                                       to=phone_number,
                                       url='outbound',
                                       _external=True)
        except Exception as e:
            app.logger.error(e)
            return jsonify({'error': str(e)})

        return jsonify({'message': 'Call incoming!'})
    else:
        import pdb; pdb.set_trace()
        return redirect('index.html')


def outbound(request):
    import ipdb; ipdb.set_trace()
    if request.method == 'POST':
        response = twiml.Response()

        # response.say("Thank you for contacting Boomerrang. If this "
        #              "were in production, we'd dial your intended target.",
        #              voice='alice')

        with response.dial() as dial:
            dial.number("+15102894755")
        return str(response)
