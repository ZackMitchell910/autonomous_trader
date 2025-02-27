# app/tasks.py
from celery import Celery
from ai_trader.trader import start_trader

celery_app = Celery('trader', broker='redis://localhost:6379/0')

@celery_app.task
def run_trader(user_data, settings):
    user = User(**user_data)
    start_trader(user, settings)