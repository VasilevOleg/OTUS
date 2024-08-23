from django.db import models


class Event(models.Model):
    date = models.DateTimeField()
    csq = models.IntegerField(null=True, blank=True)
    sv = models.IntegerField(null=True, blank=True)
    beam = models.IntegerField(null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    finish = models.DateTimeField(null=True, blank=True)
    bytes = models.BigIntegerField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Event on {self.date}"
