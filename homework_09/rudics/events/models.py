from django.db import models


class Event(models.Model):
    date = models.DateTimeField()
    csq = models.IntegerField(null=True, blank=True)
    sv = models.IntegerField(null=True, blank=True)
    beam = models.IntegerField(null=True, blank=True)
    transfer = models.CharField(max_length=10, default="DL")  # Переименованное поле
    start = models.TimeField(null=True, blank=True)
    finish = models.TimeField(null=True, blank=True)
    bytes = models.IntegerField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Event {self.date} - {self.transfer}"
