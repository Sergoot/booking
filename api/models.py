from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from .managers import ClientManager


class Client(AbstractUser):
    """ Модель клиента """
    username = None
    email = models.EmailField('Email', max_length=256,unique=True)
    phone = models.CharField('Номер телефона клиента',
                             max_length=50, blank=True)
    name = models.CharField('Имя клиента', max_length=256)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'name', 'is_staff']
    objects = ClientManager()
    CREATE_FIELDS = ['phone', 'name']

    def __str__(self) -> str:
        string = f"{self.name} {self.email}"
        if self.phone:
            return string + f" {self.phone}"
        return string


class Visit(models.Model):
    """ Модель бронирования """
    date = models.DateField('Дата бронирования', default=timezone.now)
    time_start = models.TimeField('Время начала приёма')
    time_end = models.TimeField('Время конца приёма',)
    duration = models.IntegerField('Длительность приёма(мин)', default=60)
    is_visited = models.BooleanField('Посещен ли приём', default=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')

    def __str__(self) -> str:
        return f"{self.date} ({self.time_start}-{self.time_end}) {self.client}"

