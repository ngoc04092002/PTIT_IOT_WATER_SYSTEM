import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path

from dotenv import load_dotenv  # pip install python-dotenv

import schedule
import time
from dbs import getSchedulesHTML, getItemByDate, deleteManyByDate
from datetime import datetime


PORT = 587
# Adjust server address, if you are not using @outlook
EMAIL_SERVER = "smtp.gmail.com"

# current_dir = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()

envars = ".env"
load_dotenv(envars)

# Read environment variables
sender_email = os.getenv("EMAIL")
password_email = os.getenv("PASSWORD")


def send_email(subject, receiver_email, date):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr(("NGOC", f"{sender_email}"))
    msg["To"] = receiver_email
    msg["BCC"] = sender_email

    msg.add_alternative(
        f"""\
    <html>
      <body>
        <p>Xin chào bạn,</p>
        <p>Chúc bạn một ngày tốt lành.</p>
        <p>Hôm nay bạn có lịch tưới cây vào lúc</p>
        {date}
        <p>Mong bạn hãy mở ứng dụng vào các thời gian trên.</p>
        <p>Cảm ơn bạn đã là khách hàng của chúng tôi</p>
        <p>NGOC</p>
      </body>
    </html>
    """,
        subtype="html",
    )
    with smtplib.SMTP(EMAIL_SERVER, PORT) as server:
        server.starttls()
        server.login(sender_email, password_email)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print(receiver_email+':: sended')

    return schedule.CancelJob


def send_schedyle_everyday():
    date = datetime.today().strftime('%Y-%m-%d')
    print(getItemByDate(date))
    emails = set()
    for d in getItemByDate(date):
        emails.add(d['email'])

    for email in emails:
        schedule.every().day.at("08:00").do(send_email(
        subject="Hệ thống tưới cây",
        receiver_email=email,
        date=getSchedulesHTML(email),
    ))
        
    deleteManyByDate(date)
    
    while True:
        schedule.run_pending()
        time.sleep(1)