import subprocess
import threading
import time
import logging
import json
from datetime import datetime
import os
import configparser

from connect import establish_connection, kill_pppd, clear_port
from download import download_file, get_ftp_url

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

log_file = os.path.join(config['LOCAL']['log_folder'], "main.log")
logging.basicConfig(level=logging.INFO, filename=log_file, filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")

def log_to_json(event_data):
    json_file = os.path.join(config['LOCAL']['db_folder'], "events.json")
    try:
        if not os.path.exists(json_file):
            with open(json_file, "w") as file:
                json.dump([], file)

        with open(json_file, "r+") as file:
            data = json.load(file)
            data.append(event_data)
            file.seek(0)
            json.dump(data, file, indent=4)
        logging.info("Данные успешно записаны в файл JSON.")
    except Exception as e:
        logging.error(f"Ошибка записи в файл JSON: {e}")

def ping_until_success():
    while True:
        result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            logging.info("Пинг успешен, соединение с интернетом установлено.")
            return True
        time.sleep(2)

def download_with_timeout(local_path, event_data):
    logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Начало выполнения скрипта download.py.")
    try:
        ftp_url = get_ftp_url()  # Формируем URL для FTP-сервера
        download_file(ftp_url, local_path, event_data)
    except Exception as e:
        logging.error(f"Ошибка при скачивании файла: {e}")
    finally:
        logging.info("Завершение работы потока скачивания.")

def main():
    event_data = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "csq": None,
        "sv": None,
        "beam": None,
        "start": None,
        "finish": None,
        "bytes": None,
        "duration": None,
        "speed": None
    }

    connection_thread = threading.Thread(target=establish_connection, args=(event_data,))
    connection_thread.start()

    # Ждем завершения установления соединения или истечения 60 секунд
    connection_thread.join(timeout=60)

    if connection_thread.is_alive() or not event_data["csq"]:
        logging.error("Соединение не установлено в течение 60 секунд.")
        kill_pppd()
        clear_port(config['MODEM']['port'])
        log_to_json(event_data)
        return

    if not ping_until_success():
        logging.error("Пинг не удался в течение 60 секунд.")
        kill_pppd()
        clear_port(config['MODEM']['port'])
        log_to_json(event_data)
        return

    local_path = config['LOCAL']['local_download_folder']

    # Запускаем скачивание файла с тайм-аутом 90 секунд
    download_thread = threading.Thread(target=download_with_timeout, args=(local_path, event_data))
    download_thread.start()
    download_thread.join(timeout=90)

    # Проверка завершения потока скачивания
    if download_thread.is_alive():
        logging.warning("Процесс скачивания не завершился за 90 секунд, принудительное завершение.")

    # Завершаем работу и записываем результат
    kill_pppd()
    clear_port(config['MODEM']['port'])
    log_to_json(event_data)

if __name__ == "__main__":
    main()
