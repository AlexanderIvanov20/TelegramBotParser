from django.db import models


class Comment(models.Model):
    town_from = models.CharField(max_length=500)
    town_to = models.CharField(max_length=500)
    posted = models.CharField(max_length=500)
    date = models.DateField(max_length=500)
    country_from = models.CharField(max_length=500)
    country_to = models.CharField(max_length=500)
    customer = models.CharField(max_length=500)
    customer_link = models.CharField(max_length=500)
    recipient = models.CharField(max_length=500)
    recipient_link = models.CharField(max_length=500)
    short = models.CharField(max_length=600)
