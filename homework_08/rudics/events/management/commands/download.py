import shutil
import urllib.request as request
from urllib.error import URLError, HTTPError
from contextlib import closing
import configparser
import os
from datetime import datetime
import logging

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "config.ini"))


def get_ftp_url():
    ftp_url = f"ftp://{config['FTP']['username']}:{config['FTP']['password']}@{config['FTP']['server_ip_ftp']}/{config['FTP']['download_folder']}/{config['FTP']['file_to_download']}"
    return ftp_url


def download_file(ftp_url, local_path, event_data):
    start_time = datetime.now()
    event_data["start"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
    logging.info(
        f"{event_data['start']} - Connecting to FTP server and starting file download."
    )

    try:
        timestamp = start_time.strftime("%Y%m%d_%H%M%S")

        if os.path.isdir(local_path):
            file_name = os.path.basename(ftp_url)
            new_file_name = f"{timestamp}_{file_name}"
            new_local_path = os.path.join(local_path, new_file_name)
        else:
            dir_name, file_name = os.path.split(local_path)
            new_file_name = f"{timestamp}_{file_name}"
            new_local_path = os.path.join(dir_name, new_file_name)

        with closing(request.urlopen(ftp_url)) as response:
            with open(new_local_path, "wb") as file:
                shutil.copyfileobj(response, file)
                file_size = file.tell()

        finish_time = datetime.now()
        duration = (finish_time - start_time).total_seconds()
        speed = round((file_size / 1024) / duration, 3)

        event_data.update(
            {
                "finish": finish_time.strftime("%Y-%m-%d %H:%M:%S"),
                "bytes": file_size,
                "duration": round(duration, 2),
                "speed": speed,
            }
        )

        logging.info(
            f"{event_data['finish']} - File successfully downloaded and saved at: {new_local_path}"
        )
    except HTTPError as e:
        logging.error(f"HTTP error during file download: {e.code} - {e.reason}")
    except URLError as e:
        logging.error(f"URL error during file download: {e.reason}")
    except OSError as e:
        logging.error(f"Error saving file: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        event_data["finish"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
