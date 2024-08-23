import json
import os
from django.core.management.base import BaseCommand
from events.models import Event


class Command(BaseCommand):
    help = "Imports events from events.json into the Django database"

    def handle(self, *args, **kwargs):
        json_file_path = os.path.join(
            os.path.dirname(__file__), "../../../db/events.json"
        )

        try:
            with open(json_file_path, "r") as file:
                events_data = json.load(file)
                for event in events_data:
                    Event.objects.update_or_create(
                        date=event["date"],
                        defaults={
                            "csq": event.get("csq"),
                            "sv": event.get("sv"),
                            "beam": event.get("beam"),
                            "start": event.get("start"),
                            "finish": event.get("finish"),
                            "bytes": event.get("bytes"),
                            "duration": event.get("duration"),
                            "speed": event.get("speed"),
                        },
                    )
            self.stdout.write(
                self.style.SUCCESS("Successfully imported events from JSON file")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error importing events: {e}"))
