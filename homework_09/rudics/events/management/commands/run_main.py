from django.core.management.base import BaseCommand
import subprocess
import threading
import time
import logging
import json
from datetime import datetime
import os
import configparser

from events.management.commands.connect import establish_connection, kill_pppd, clear_port
from events.management.commands.download import download_file, get_ftp_url
from events.models import Event

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '../../config.ini'))

log_file = os.path.join(config['LOCAL']['log_folder'], "main.log")
logging.basicConfig(level=logging.INFO, filename=log_file, filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")

def log_to_json(event_data):
    json_file = config['LOCAL']['json_file']
    try:
        if not os.path.exists(json_file):
            with open(json_file, "w") as file:
                json.dump([], file)

        with open(json_file, "r+") as file:
            data = json.load(file)
            data.append(event_data)
            file.seek(0)
            json.dump(data, file, indent=4)
        logging.info("Data successfully written to JSON file.")
        print("Data successfully written to JSON file.")
    except Exception as e:
        logging.error(f"Error writing to JSON file: {e}")
        print(f"Error writing to JSON file: {e}")

def import_latest_event():
    json_file = config['LOCAL']['json_file']
    try:
        with open(json_file, "r") as file:
            data = json.load(file)
            latest_event = data[-1]

            if not Event.objects.filter(date=latest_event['date'], csq=latest_event['csq']).exists():
                Event.objects.create(
                    date=latest_event['date'],
                    csq=latest_event['csq'],
                    sv=int(latest_event['sv']),
                    beam=int(latest_event['beam']),
                    transfer=latest_event['transfer'],
                    start=latest_event['start'],
                    finish=latest_event['finish'],
                    bytes=latest_event['bytes'],
                    duration=latest_event['duration'],
                    speed=latest_event['speed']
                )
                logging.info("Latest event successfully imported into the database.")
                print("Latest event successfully imported into the database.")
            else:
                logging.info("Duplicate event found. Skipping import.")
                print("Duplicate event found. Skipping import.")
    except Exception as e:
        logging.error(f"Error importing latest event: {e}")
        print(f"Error importing latest event: {e}")

def ping_until_success():
    while True:
        result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            logging.info("Ping successful, internet connection established.")
            return True
        time.sleep(2)

def download_with_timeout(local_path, event_data):
    logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Starting download.py script.")
    try:
        ftp_url = get_ftp_url()
        download_file(ftp_url, local_path, event_data)
    except Exception as e:
        logging.error(f"Error during file download: {e}")

def stop_all_processes():
    try:
        kill_pppd()
        clear_port(config['MODEM']['port'])
    except Exception as e:
        logging.error(f"Error during cleanup: {e}")
    finally:
        logging.info("All processes stopped.")

def main():
    event_data = {
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

    try:
        connection_thread = threading.Thread(target=establish_connection, args=(event_data,))
        connection_thread.start()
        connection_thread.join(timeout=60)

        if connection_thread.is_alive() or not event_data["csq"]:
            logging.error("Connection not established within 60 seconds.")
            log_to_json(event_data)
            stop_all_processes()
            import_latest_event()
            return

        if not ping_until_success():
            logging.error("Ping failed within 60 seconds.")
            log_to_json(event_data)
            stop_all_processes()
            import_latest_event()
            return

        local_path = config['LOCAL']['local_download_folder']

        download_thread = threading.Thread(target=download_with_timeout, args=(local_path, event_data))
        download_thread.start()
        download_thread.join(timeout=90)

        if download_thread.is_alive():
            logging.warning("Download process did not complete within 90 seconds, forcing termination.")
            log_to_json(event_data)
            stop_all_processes()
            import_latest_event()
            return
        
    except RuntimeError as e:
        logging.error(f"Runtime error: {e}")
        log_to_json(event_data)
    finally:
        log_to_json(event_data)
        stop_all_processes()
        import_latest_event()

class Command(BaseCommand):
    help = 'Run main process for downloading files and connecting to server'

    def handle(self, *args, **kwargs):
        main()
