import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pymongo import MongoClient
import datetime
import time

mongo = MongoClient('localhost', 27017)
main_db = mongo['lbec2024']
calendar_data = main_db['calendar_data']

def send_mail(target, title, start):
    # setup the parameters of the message
    password = "tzey tmxx ocgr ltmw"
    from_addr = "spotifyzao111"
    to_addr = target
    subject = "LBEC2024 Notification"

    # setup the MIME
    message = MIMEMultipart()
    message['From'] = from_addr
    message['To'] = to_addr
    message['Subject'] = subject

    # add in the message body
    message.attach(MIMEText(f"{title} is starting at {start}", 'plain'))

    # create server
    server = smtplib.SMTP('smtp.gmail.com: 587')

    server.starttls()

    # Login Credentials for sending the mail
    server.login(message['From'], password)

    # send the message via the server
    server.sendmail(from_addr, to_addr, message.as_string())

    server.quit()

    print("Successfully sent email to %s:" % (message['To']))

while True:
    to_notify = calendar_data.find({"toNotify": True})
    for entry in to_notify:
        entry_date = datetime.datetime.strptime(entry["start"], "%Y-%m-%dT%H:%M:%S+00:00")
        notify_timing = entry["notifyTiming"]
        current_time = datetime.datetime.now()

        # check if current time is within entry["notifyTiming"] minutes of entry["date"]
        if (entry_date - current_time).total_seconds() / 60 <= notify_timing:
            send_mail(entry["email"], entry["title"], entry["start"])

    time.sleep(300) # sleep for 5 minutes