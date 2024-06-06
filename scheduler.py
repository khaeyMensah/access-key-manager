import schedule
import time
import os

def update_key_statuses():
    os.system('python manage.py update_key_statuses')

# Schedule the task to run daily
schedule.every().day.at("00:00").do(update_key_statuses)

while True:
    schedule.run_pending()
    time.sleep(60)  # wait one minute
