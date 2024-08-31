import json
from django.core.management.base import BaseCommand
from events.models import Event
import configparser
import os

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "../../config.ini"))


class Command(BaseCommand):
    help = "Import events from a JSON file."

    def handle(self, *args, **options):
        json_file_path = config["LOCAL"]["json_file"]
        try:
            with open(json_file_path) as f:
                events_data = json.load(f)
                for event_data in events_data:
                    Event.objects.create(
                        date=event_data["date"],
                        csq=event_data["csq"],
                        sv=event_data["sv"],
                        beam=event_data["beam"],
                        transfer=event_data["transfer"],
                        start=event_data["start"],
                        finish=event_data["finish"],
                        bytes=event_data["bytes"],
                        duration=event_data["duration"],
                        speed=event_data["speed"],
                    )
            self.stdout.write(self.style.SUCCESS("Successfully imported events."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error importing events: {e}"))
