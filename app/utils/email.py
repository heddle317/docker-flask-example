import pystmark

from app import config


def send_invite(user):
    subject = 'You have been invited to sign up for MakeMeUp Amin Panel!'
    body = 'Click here to accept your invitation to deploy.makemeup.co.' \
           '\n\n{}/accept_invite/{}'.format(config.APP_BASE_LINK, user.email_verification_token)
    send_email(user.email, subject, body)


def send_email(email, subject, body):
    # Send a single message
    message = pystmark.Message(sender=config.SENDER_EMAIL,
                               to=email,
                               subject=subject,
                               text=body)
    pystmark.send(message, api_key=config.POSTMARKAPP_API_KEY)
