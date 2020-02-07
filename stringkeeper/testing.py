import os, time, random, smtplib, shutil, imaplib, email, calendar, json
import os
import random
import string

from email.message import EmailMessage

def test_stringkeeper():
    #blackmesanetwork.com
    to_email = 'andredoumad@gmail.com'
    EMAIL_ADDRESS = 'AKIAYZ2XE524B2NTG7DI'
    EMAIL_PASSWORD = 'BGJsy/NhlXE1x8HM8b6VGSuFXjwmfWmYYk5qntB0iwlw'

    msg = EmailMessage()
    msg['Subject'] = 'Test subject line'
    msg['From'] = 'andre@stringkeeper.com'
    msg['To'] = to_email
    msg.set_content('test msg content')

    with smtplib.SMTP('email-smtp.us-west-2.amazonaws.com', 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

# test_stringkeeper()




def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))



random_string = random_string_generator(20)

print(random_string)
