from django.db import models

# Create your models here.
class List(models.Model):
    line = models.IntegerField()
    time = models.TimeField()
    title = models.CharField(max_length=30)
    distance = models.FloatField()

    def __str__(self):
        return self.title



