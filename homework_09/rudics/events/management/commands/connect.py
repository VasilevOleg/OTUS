import subprocess
import time
import logging
import re
import os
from datetime import datetime
import configparser

config = configparser.ConfigParser()
config_file_path = "/home/pi/rudics/events/config.ini"
config.read(config_file_path)


def get_wvdial_log_filename():
    today = datetime.now().strftime("%Y%m%d")
    log_filename = f"{today}_wvdial.log"
    return os.path.join(config["LOCAL"]["log_folder"], log_filename)


log_file = get_wvdial_log_filename()
logging.basicConfig(
    level=logging.INFO,
    filename=log_file,
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def clear_port(port):
    logging.info(f"Attempting to clear port {port}...")
    try:
        result = subprocess.run(
            ["sudo", "fuser", "-k", port],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        logging.info(f"Port {port} cleared successfully: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to clear port {port}: {e.stderr.strip()}")

    time.sleep(1)


def kill_pppd():
    logging.info("Terminating all existing PPP connections...")
    subprocess.run(
        ["sudo", "killall", "pppd"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    time.sleep(3)

    for _ in range(1):
        check_result = subprocess.run(
            ["sudo", "fuser",  "-k", config["MODEM"]["port"]],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        if not check_result.stdout.strip():
            logging.info(f"{config['MODEM']['port']} is free for use.")
            return
        logging.warning(
            f"{config['MODEM']['port']} is still busy. Retrying in 2 seconds..."
        )
        time.sleep(2)

    logging.error(f"{config['MODEM']['port']} is still occupied by another process.")
    raise RuntimeError("The device is busy, cannot start wvdial.")


def run_wvdial():
    logging.info("Starting wvdial...")
    with open(log_file, "w") as logfile:
        process = subprocess.Popen(
            ["sudo", "wvdial"],
            stdout=logfile,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        return process


def extract_csq(line):
    csq_match = re.search(r"\+CSQ:(\d+)", line)
    if csq_match:
        csq = int(csq_match.group(1))
        if 1 <= csq <= 5:
            logging.info(f"CSQ = {csq}")
            return csq
    return 0


def extract_sv_beam(line):
    cier_match = re.search(r"\+CIEV:3,(\d+),(\d+),\d+,\d+,\d+", line)
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

            time.sleep(0.5)

    logging.info(
        f"CSQ, SV, BEAM values extracted: CSQ={csq_value}, SV={sv_value}, BEAM={beam_value}"
    )
    return csq_value, sv_value, beam_value


def establish_connection(event_data):
    clear_port(config["MODEM"]["port"])
    kill_pppd()

    wvdial_process = run_wvdial()

    try:
        csq, sv, beam = read_log_for_csq_sv_beam()
        event_data["csq"] = csq
        event_data["sv"] = sv
        event_data["beam"] = beam

        return wvdial_process
    except Exception as e:
        logging.error(f"Error establishing connection: {e}")
        return None
