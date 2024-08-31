import unittest
import logging
import sys
import os
from datetime import datetime

# Добавляем корневую папку проекта в sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rudics.settings')
import django
django.setup()  # Инициализируем Django

from events.management.commands.connect import establish_connection, kill_pppd, clear_port
from events.models import Event

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class TestConnection(unittest.TestCase):
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
        self.test_event = Event.objects.create(
            date=self.event_data["date"],
            csq=0,
            sv=0,
            beam=0,
            transfer="DL",
            start="00:00:00"
        )
        logging.info("Test environment setup completed.")

    def test_establish_connection(self):
        logging.info("Testing connection establishment...")
        try:
            establish_connection(self.event_data)
            self.assertIsNotNone(self.event_data["csq"], "CSQ value should not be None.")
            self.assertIsNotNone(self.event_data["sv"], "SV value should not be None.")
            self.assertIsNotNone(self.event_data["beam"], "BEAM value should not be None.")
            logging.info(f"Connection established with CSQ={self.event_data['csq']}, SV={self.event_data['sv']}, BEAM={self.event_data['beam']}.")
        except Exception as e:
            logging.error(f"Connection test failed: {e}")
            self.fail(f"Connection establishment failed: {e}")

    def test_clear_port(self):
        logging.info("Testing port clearance...")
        try:
            clear_port("/dev/ttyUSB0")
            logging.info("Port cleared successfully.")
        except Exception as e:
            logging.error(f"Clear port test failed: {e}")
            self.fail(f"Port clearance failed: {e}")

    def tearDown(self):
        try:
            self.test_event.delete()
            kill_pppd()
            logging.info("Test environment teardown completed.")
        except Exception as e:
            logging.error(f"Error during teardown: {e}")

if __name__ == "__main__":
    unittest.main()
