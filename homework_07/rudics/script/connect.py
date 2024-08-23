import subprocess
import time
import logging
import re
import os
from datetime import datetime
import configparser

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

def get_wvdial_log_filename():
    today = datetime.now().strftime("%Y%m%d")
    log_filename = f"{today}_wvdial.log"
    return os.path.join(config['LOCAL']['log_folder'], log_filename)

log_file = get_wvdial_log_filename()
logging.basicConfig(level=logging.INFO, filename=log_file, filemode="a", 
                    format="%(asctime)s - %(levelname)s - %(message)s")

def clear_port(port):
    """Принудительно завершает все процессы, использующие указанный порт."""
    logging.info(f"Попытка освободить порт {port}...")
    try:
        result = subprocess.run(["sudo", "fuser", "-k", port], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logging.info(f"Порт {port} успешно освобожден: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Ошибка при освобождении порта {port}: {e.stderr.strip()}")

    time.sleep(1)  # Даем немного времени на завершение процессов

def kill_pppd():
    """Удаляет все существующие PPP-соединения и проверяет, что устройство свободно."""
    logging.info("Прерывание всех существующих PPP-соединений...")
    subprocess.run(['sudo', 'killall', 'pppd'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    time.sleep(3)  # Увеличенное время ожидания до 5 секунд

    # Проверка, что устройство не занято
    for _ in range(1):  # 1 попытка проверки порта
        check_result = subprocess.run(['sudo', 'fuser', config['MODEM']['port']], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if not check_result.stdout.strip():
            logging.info(f"{config['MODEM']['port']} свободно для использования.")
            return
        logging.warning(f"{config['MODEM']['port']} все еще занято. Повторная попытка через 2 секунды...")
        time.sleep(2)

    logging.error(f"{config['MODEM']['port']} все еще занято другим процессом.")
    raise RuntimeError("Устройство занято, не могу запустить wvdial.")

def run_wvdial():
    """Запускает wvdial и пишет лог в файл."""
    logging.info("Запуск wvdial...")
    with open(log_file, "w") as logfile:
        process = subprocess.Popen(['sudo', 'wvdial'], stdout=logfile, stderr=subprocess.STDOUT, universal_newlines=True)
        return process

def extract_csq(line):
    csq_match = re.search(r'\+CSQ:(\d+)', line)
    if csq_match:
        csq = int(csq_match.group(1))
        if 1 <= csq <= 5:
            logging.info(f"CSQ = {csq}")
            return csq
    return 0

def extract_sv_beam(line):
    cier_match = re.search(r'\+CIEV:3,(\d+),(\d+),\d+,\d+,\d+', line)
    if cier_match:
        sv_value = cier_match.group(1)
        beam_value = cier_match.group(2)
        logging.info(f"SV = {sv_value}, BEAM = {beam_value}")
        return sv_value, beam_value
    return None, None

def read_log_for_csq_sv_beam():
    csq_value = 0
    sv_value = None
    beam_value = None

    with open(log_file, "r") as logfile:
        logfile.seek(0, os.SEEK_END)

        while True:
            line = logfile.readline().strip()
            if line:
                if not csq_value:
                    csq_value = extract_csq(line)
                if not (sv_value and beam_value):
                    sv_value, beam_value = extract_sv_beam(line)

                if csq_value and sv_value and beam_value:
                    break

            time.sleep(0.5)  # Синхронное ожидание

    logging.info(f"Значения CSQ, SV, BEAM извлечены: CSQ={csq_value}, SV={sv_value}, BEAM={beam_value}")
    return csq_value, sv_value, beam_value

def establish_connection(event_data):
    clear_port(config['MODEM']['port'])
    kill_pppd()
    
    wvdial_process = run_wvdial()

    try:
        csq, sv, beam = read_log_for_csq_sv_beam()
        event_data["csq"] = csq
        event_data["sv"] = sv
        event_data["beam"] = beam

        return wvdial_process
    except Exception as e:
        logging.error(f"Ошибка при установлении соединения: {e}")
        return None
