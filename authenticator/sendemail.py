import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = "lsmauth@gmail.com" 
sender_password = "fvfe wkjr hhdr hdov" 

def generate_code(length=6):
    characters = string.digits 
    code = ''.join(random.choice(characters) for _ in range(length))
    return code

def send_code_email(recipient_email, code): 
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = 'Your Authentication Code'

    body = f"Your authentication code is: {code}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()

        print(f"Code sent to {recipient_email}")
        return code

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return None

def send_notification_block(recipient_email):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = 'Your Account is Blocked'

    body = f"Your account has been blocked due to multiple failed login attempts. Please try again later."
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()

        print(f"Notification sent to {recipient_email}")

    except Exception as e:
        print(f"Error sending email: {str(e)}")

def send_notification_login(recipient_email):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = 'Login Notification'

    body = f"Your account has been accessed. If this was not you, please change your password."
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()

        print(f"Notification sent to {recipient_email}")

    except Exception as e:
        print(f"Error sending email: {str(e)}")
