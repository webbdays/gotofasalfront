import smtplib
from email.message import EmailMessage
import ssl
import os
import jwt
import datetime

# global
sender = "gotofasalfront@gmail.com"

def send_email(sender, receiver, subject, body):
    
    print("sending email")
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.set_content(body)
    sslctx = ssl.create_default_context()
    print("sending email")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=sslctx) as smtp:
        print("logging in to email")
        smtp.login(sender, os.getenv("GMAIL_APP_PASSWORD"))
        smtp.sendmail(sender, receiver, msg.as_string())
    print("sent email")

def verify_user_email_token_generator(user_email):
        print("verify token ")
        token = jwt.encode({"email":user_email, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5)}, os.getenv("EMAIL_VERIFY_MAIN_SECRET"))
        subject = "User Email Verification"
        body = "Verification Token: " + token + "\nToken is valid for around 2 minutes."
        send_email(sender, user_email, subject, body)

