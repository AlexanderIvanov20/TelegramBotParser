from django.db import models

# Create your models here.


class Profile(models.Model):
    vip = models.BooleanField()
    activation_date = models.FloatField()
    activation_till = models.FloatField()

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return (f'Профиль пользователя {self.user}')
