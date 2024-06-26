import streamlit as st
import pandas as pd
import schedule
import threading
from songline import Sendline
import pytz
import time
from datetime import datetime

# Define Bangkok timezone
BANGKOK_TIMEZONE = pytz.timezone('Asia/Bangkok')

def send_line_notification(messenger, message):
    messenger.sendtext(message)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)  # to prevent this loop from consuming too much CPU

# Scheduler thread handling
if not any([isinstance(t, threading.Thread) and t.name == 'SchedulerThread' for t in threading.enumerate()]):
    scheduler_thread = threading.Thread(target=run_scheduler, name='SchedulerThread')
    scheduler_thread.start()

def read_and_schedule(df, messenger):
    for index, row in df.iterrows():
        title = row['Title']
        description = row['Description']
        hour = row['Hour']
        minute = row['Minute']
        everyday = row['Everyday Notify'] == 'Yes'

        # Format time using the hour and minute columns
        notification_time = f"{int(hour):02}:{int(minute):02}"

        # Schedule the message with title and description
        message = f"Title: {title}\nDescription: {description}"
        if everyday:
            schedule.every().day.at(notification_time).do(send_line_notification, messenger, message)
        else:
            job = schedule.every().day.at(notification_time).do(send_line_notification, messenger, message)
            schedule.every().day.at(notification_time).do(lambda job=job: schedule.cancel_job(job))

        st.write(f"Scheduled '{message}' at {notification_time} - {'Everyday' if everyday else 'Once'}")

st.title("LINE Notification Scheduler")
line_token = st.text_input("Enter your LINE API Token", type="password")

if line_token:
    messenger = Sendline(line_token)
    uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        read_and_schedule(df, messenger)
        st.success("Notifications scheduled based on uploaded file.")

st.write("Note: Restart the app to clear the scheduler if needed.")
