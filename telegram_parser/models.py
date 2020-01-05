from django.db import models

# Create your models here.
class Comment(models.Model):
    route = models.CharField()
    posted = models.CharField()
    date = models.DateField()
    destination = models.CharField()
    author = models.CharField()
    recipient = models.CharField()
