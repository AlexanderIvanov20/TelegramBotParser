from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Activation(models.Model):
    id_user = models.IntegerField()
    purchase_date = models.FloatField()
    activation_till = models.FloatField()
    provider_payment_charge_id = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Активация'
        verbose_name_plural = 'Активации'

        db_table = 'activations'

    def __str__(self):
        return f'Активация № {self.provider_payment_charge_id}'


class Profile(models.Model):
    id_user = models.IntegerField()
    vip = models.BooleanField()
    subscription = models.BooleanField()
    activation_date = models.FloatField()
    activation_till = models.FloatField()
    need_vip = models.BooleanField()

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

        db_table = 'profiles'

    def __str__(self):
        return (f'Профиль пользователя {self.id_user}')
