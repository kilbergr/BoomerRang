import argparse
import os

from django.core.exceptions import MiddlewareNotUsed
from twilio.rest import Client


def load_twilio_config():
    twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_number = os.environ.get('TWILIO_NUMBER')

    if not all([twilio_account_sid, twilio_auth_token, twilio_number]):
        print('Twilio auth info not configured.')
        raise MiddlewareNotUsed

    return (twilio_number, twilio_account_sid, twilio_auth_token)


class MessageClient(object):
    def __init__(self):
        (twilio_number, twilio_account_sid,
         twilio_auth_token) = load_twilio_config()

        self.twilio_number = twilio_number
        self.twilio_client = Client(twilio_account_sid,
                                              twilio_auth_token)

    def send_message(self, body, to):
        self.twilio_client.messages.create(body=body, to=to,
                                           from_=self.twilio_number,
                                           media_url=['https://demo.twilio.com/owl.png']
                                           )

def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('dest_number', type=str, nargs=1, help='number to text.')
	return parser.parse_args()

def main():
	args = get_args()

	message_client = MessageClient()
	num_to_send = args.dest_number[0] if args.dest_number else '(555) 555-5555'
	message_client.send_message("Hello, this is a test message.", num_to_send)

if __name__=='__main__':
	main()
