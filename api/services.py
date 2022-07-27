import random
from ast import literal_eval
from datetime import datetime, date, timedelta, time

from django.core.mail import send_mail
from django.db.models.base import Model
from django.db.models import QuerySet
from typing import Any

from booking import settings
from .models import Visit


def get_all_or_filter(model: Model, **filters: Any) -> QuerySet:
    """ Возвращает QuerySet со всеми атрибутами модели или отфильтрованными по фильтрам атрибутами """
    return model.objects.filter(**filters) if filters else model.objects.all()


def get_or_create(model: Model, **fields: Any) -> tuple:
    """ Возваращет найденную модель пользователя или только что созданную """
    return model.objects.get_or_create(**fields)


def generate_password() -> str:
    """ генерирует пароль для нового пользователя """
    symbols = 'abcdefghijklmnopqrstuvwxyz?&$#@!()*-+_.'
    symbols = tuple(symbols + symbols[:27:].upper() + ''.join(map(str, [i for i in range(10)])))
    return ''.join(random.sample(symbols, 10))


def check_booking_time(date_: str, time_start: str, duration: int = 60) -> bool:
    """ Проверяет свободно ли данное время для записи """
    time_end = custom_timedelta(time_start, duration)
    time_pre_start = custom_timedelta(time_start, duration, True)
    return list((Visit.objects.filter(date=date_, time_start__gte=time_pre_start, time_start__lte=time_end))) == []


def get_end_time(start_time: str, duration: int = 60) -> str:
    """ Возвращает время окончания приёма """
    return custom_timedelta(start_time, duration).strftime("%H:%M")


def custom_timedelta(time_: str, duration: int = 60, *action: bool) -> time:
    """ Прибавляет/убавляет время у time """
    time_ = datetime.strptime(time_, "%H:%M").time()
    return (datetime.combine(date(1, 1, 1), time_)-timedelta(minutes=duration)).time() if action \
        else (datetime.combine(date(1, 1, 1), time_)+timedelta(minutes=duration)).time()


def get_list_date_time(date_list: str, time_list: str) -> tuple:
    return tuple(literal_eval(date_list)), tuple(literal_eval(time_list))


def mail(email: str, password: str = None, **kwargs: any) -> None:
    """ Отправляет на почту напоминание о дедлайне по задаче """
    subject = f'Приветсвуем вас, {email}'
    message = f'Ваш пароль: {password}'
    if kwargs:
        date_ = kwargs.get('date')
        time_start = kwargs.get('time_start')
        subject = f'Здравствуйте, {email}'
        message = f'Вы получили это письмо, потому что записались на прием ' \
                  f'{date_} в {time_start}, не забудьте)'
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, [email], fail_silently=False)
