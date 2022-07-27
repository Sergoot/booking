from booking.celery import app
from .services import mail


@app.task
def send_email(email, password=None, **kwargs):
    mail(email, password, **kwargs)
