import twilio

from app import config

from twilio.rest import TwilioRestClient


def send_text(number, message):
    client = TwilioRestClient(config.TWILIO_SID, config.TWILIO_SECRET)
    try:
        message = client.messages.create(body=message,
                                         to=number,
                                         from_=config.TWILIO_FROM)
    except twilio.TwilioRestException as e:
        print e
