from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

def account_activation_email(email,email_token):
    subject = 'Activate your account'
    email_from = settings.DEFAULT_FROM_EMAIL

    activation_link = f"{settings.SITE_URL}/accounts/activate/?token={email_token}"

    html_message = render_to_string('email/activation_email.html', {'activation_link': activation_link})
    plain_text = f"Hi , Please verify the account activation link: {activation_link}"

    send_mail(subject,
              plain_text,
              email_from, [email],
              html_message=html_message)