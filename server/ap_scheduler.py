from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
from .models import ImageModel


def clear_todays_data():
    ImageModel.objects.values().update(today_looked=0, today_good=0)
    print("Cleared today's data at " + str(datetime.now()))


def clear_hour_data():
    ImageModel.objects.values().update(hour_looked=0, hour_good=0)
    print("Cleared today's data at " + str(datetime.now()))


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(clear_todays_data, 'cron', hour=15, minute=00)
    scheduler.add_job(clear_hour_data, 'cron', minute=00)
    scheduler.start()
