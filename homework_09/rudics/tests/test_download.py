import unittest
import logging
import sys
import os
from datetime import datetime
import configparser

# Добавляем корневую папку проекта в sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rudics.settings')
import django
django.setup()  # Инициализируем Django

from events.management.commands.download import download_file, get_ftp_url
from events.models import Event

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '../events/config.ini'))

class TestDownload(unittest.TestCase):
    def setUp(self):
        self.event_data = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "csq": None,
            "sv": None,
            "beam": None,
            "transfer": "DL",
            "start": None,
            "finish": None,
            "bytes": None,
            "duration": None,
            "speed": None
        }
        self.local_path = config['LOCAL']['local_download_folder']
        self.test_event = Event.objects.create(
            date=self.event_data["date"],
            csq=0,
            sv=0,
            beam=0,
            transfer="DL",
            start="00:00:00"
        )
        logging.info("Test environment setup completed.")

    def test_download_file(self):
        logging.info("Testing file download...")
        try:
            ftp_url = get_ftp_url()
            download_file(ftp_url, self.local_path, self.event_data)
            self.assertIsNotNone(self.event_data["bytes"], "Downloaded bytes should not be None.")
            self.assertIsNotNone(self.event_data["duration"], "Download duration should not be None.")
            self.assertIsNotNone(self.event_data["speed"], "Download speed should not be None.")
            logging.info(f"File downloaded successfully: {self.event_data['bytes']} bytes, Duration: {self.event_data['duration']} seconds, Speed: {self.event_data['speed']} kB/s.")
        except Exception as e:
            logging.error(f"Download test failed: {e}")
            self.fail(f"Download failed: {e}")

    def tearDown(self):
        try:
            self.test_event.delete()
            logging.info("Test environment teardown completed.")
        except Exception as e:
            logging.error(f"Error during teardown: {e}")

if __name__ == "__main__":
    unittest.main()
