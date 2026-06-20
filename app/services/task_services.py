import random
import smtplib
import datetime as dt
from ..config import settings


def notify_assignee(assignee_email: str, task_title: str):
    now=dt.datetime.now()
    print(f" Sending email to {assignee_email}: You have been assigned to '{task_title}'")
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(settings.my_email,settings.my_password)
        connection.sendmail(from_addr=settings.my_email,to_addrs=assignee_email,msg=f"Subject:New Task Assigned\n\n{task_title} \n assigned date:{now}")