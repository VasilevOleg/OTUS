import json
from django.core.management.base import BaseCommand
from myapp.models import Event

class Command(BaseCommand):
    help = 'Imports events from JSON file'

    def handle(self, *args, **kwargs):
        with open('/home/oleg/PycharmProjects/OTUS/homework_07/rudics/db/events.json') as f:
            events = json.load(f)
            for event in events:
                Event.objects.create(
                    date=event['date'],
                    csq=event.get('csq'),
                    sv=event.get('sv'),
                    beam=event.get('beam'),
                    start=event.get('start'),
                    finish=event.get('finish'),
                    bytes=event.get('bytes'),
                    duration=event.get('duration'),
                    speed=event.get('speed')
                )
        self.stdout.write(self.style.SUCCESS('Events imported successfully!'))
