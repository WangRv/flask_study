from extension import mail
from flask_mail import Message
from flask import render_template


def send_mail_with_html(subject, to, user, token, template):
    html_text = render_template(template, user=user, token=token)
    email_message = Message(subject=subject, recipients=[to], html=html_text)
    mail.send(message=email_message)


def send_token_confirm_email(user, token, to=None):
    send_mail_with_html("Mail confirm", to=to or user.email, user=user, token=token, template="emails/confirm.html")


def send_reset_password_email(user, token, to=None):
    send_mail_with_html("Reset password", to=to or user.email, user=user, token=token,
                        template="emails/reset_password.html")
