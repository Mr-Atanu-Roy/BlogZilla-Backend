from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import timezone


from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type

import uuid
from threading import Thread



class BaseModel(models.Model):
    
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


#for sending emails
class SendEmail(Thread):
    '''
    Using threads to send mails
    '''
    
    def __init__(self, subject, message, *receiver):

        self.recipient_list = [emails for emails in receiver]
        
        self.subject = subject.capitalize()
        self.message = message
        self.sender = settings.EMAIL_HOST_USER

        Thread.__init__(self)
        
    def run(self):
        send_mail(subject=self.subject, message=self.message, from_email=self.sender, recipient_list=self.recipient_list)


#for generating tokens for email verification
class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            text_type(user.pk) + text_type(timestamp) +
            text_type(user.is_verified)
        )
  


#global class for sending different kinds of emails
class EmailSender:
    
    def __init__(self, email):
        self.email = email


    #for sending email
    def send_email(self, subject, message):
        SendEmail(subject, message, self.email).start()


    #for sending link for email verification
    def email_verify_link_send(self, user, name):

        subject = "Verify Your Email"
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = TokenGenerator().make_token(user)
        url = f"http://127.0.0.1:8000/auth/email-verification/{uidb64}/{token}"
        current_time = timezone.now()

        message = f"Welcome to BlogZilla {name}.\n\nThere was a signin request from your email {self.email} on our site on {current_time.date()} at {current_time.time()}.\nTo continue any further operation using this email you need to verify it.\nPlease click on the link below to verify your email: {self.email}: \n{url} \n\nThankyou for joining us.\n\nRegards,\nBlogZilla Team"

        self.send_email(subject, message)


    #for sending confirmation mail after email verification
    def email_verify_notify(self):
        subject = "Email Verification Successful"
        current_time = timezone.now()

        message = f"Your email: {self.email} was verified on {current_time.date()} at {current_time.time()}.\nNow you can login to your account and post articles, read articles and do all the fun.\nLogin here: http://127.0.0.1:8000/auth/login/ \n\nThankyou for joining us.\n\nRegards,\nBlogZilla Team"

        self.send_email(subject, message)

    
    #for sending link for reseating password
    def reset_password_link_send(self, user, name, token):
        subject = "Reset your password"
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        url = f"http://127.0.0.1:8000/auth/reset-password/{uidb64}/{token}"
        current_time = timezone.now()

        message = f"Hello {name}.\nThere was a password reset request from your email- {self.email} on {current_time.date()} at {current_time.time()}.\n Please click on the link below to reset your password:\n{url}.\nIf this wasn't you, then please ignore this. This link will be invalid after 10 minutes. \n\nThankyou for joining us.\n\nRegards,\nBlogZilla Team"

        self.send_email(subject, message)


    #for sending confirmation email after password is reset
    def reset_password_notify(self):
        subject = "Password was changed"
        current_time = timezone.now()

        message = f"This email is to inform you that password for email: {self.email} was changed on {current_time.date()} at {current_time.time()}.\nIf this wasn't you then you can change your password again. \n\nThankyou for joining us.\n\nRegards,\nBlogZilla Team"

        self.send_email(subject, message)

