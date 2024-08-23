import shutil
import urllib.request as request
from urllib.error import URLError, HTTPError
from contextlib import closing
import configparser
import os
from datetime import datetime
import logging

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

def get_ftp_url():
    """Формирует URL для подключения к FTP-серверу."""
    ftp_url = f"ftp://{config['FTP']['username']}:{config['FTP']['password']}@{config['FTP']['server_ip_ftp']}/{config['FTP']['download_folder']}/{config['FTP']['file_to_download']}"
    return ftp_url

def download_file(ftp_url, local_path, event_data):

    start_time = datetime.now()
    event_data["start"] = start_time.strftime("%Y-%m-%d %H:%M:%S")  # Время начала скачивания файла
    logging.info(f"{event_data['start']} - Подключение к FTP-серверу и начало скачивания файла.")

    try:
        timestamp = start_time.strftime('%Y%m%d_%H%M%S')
        
        # Разделение пути на директорию и имя файла
        if os.path.isdir(local_path):
            # Если local_path - директория, берем имя файла из URL
            file_name = os.path.basename(ftp_url)
            new_file_name = f"{timestamp}_{file_name}"
            new_local_path = os.path.join(local_path, new_file_name)
        else:
            # Если local_path содержит имя файла, добавляем к нему временную метку
            dir_name, file_name = os.path.split(local_path)
            new_file_name = f"{timestamp}_{file_name}"
            new_local_path = os.path.join(dir_name, new_file_name)
        
        # Загрузка файла и сохранение его с новым именем
        with closing(request.urlopen(ftp_url)) as response:
            with open(new_local_path, 'wb') as file:
                shutil.copyfileobj(response, file)
                file_size = file.tell()
        
        finish_time = datetime.now()
        duration = (finish_time - start_time).total_seconds()
        speed = round((file_size / 1024) / duration, 3)
        
        # Обновление данных события
        event_data.update({
            "finish": finish_time.strftime("%Y-%m-%d %H:%M:%S"),
            "bytes": file_size,
            "duration": round(duration, 2),
            "speed": speed
        })

        logging.info(f"{event_data['finish']} - Файл успешно загружен и сохранён по пути: {new_local_path}")
    except HTTPError as e:
        logging.error(f"HTTP ошибка при загрузке файла: {e.code} - {e.reason}")
    except URLError as e:
        logging.error(f"Ошибка URL при загрузке файла: {e.reason}")
    except OSError as e:
        logging.error(f"Ошибка при сохранении файла: {e}")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
    finally:
        event_data["finish"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
