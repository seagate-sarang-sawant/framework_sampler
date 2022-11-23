# -*- coding: utf-8 -*-
"""
Locust runner file
"""
import os
import argparse
import logging
import time
import sys
import configparser
from commons.utils.system_utils import run_local_cmd
from commons import log

LOGGER = logging.getLogger(__name__)
log.initialize_loghandler(LOGGER, logging.DEBUG)


def check_log_file_errors(file_path, errors):
    """
    Function to find out error is reported in given file or not
    :param str file_path: the file in which error is to be searched
    :param list errors: error strings to be searched for
    :return: errorFound: True (if error is seen) else False
    :rtype: Boolean
    """
    error_found = False
    LOGGER.info("Debug: Log File Path %s", file_path)
    with open(file_path, "r") as log_file:
        for line in log_file:
            for error in errors:
                if error.lower() in line.lower():
                    error_found = True
                    LOGGER.info("checkLogFileError: Error Found in Locust Run : %s", line)
                    return error_found

    LOGGER.info("No Error Found")
    return error_found


def main():
    LOCUST_CFG = configparser.ConfigParser()
    LOCUST_CFG.read('locust_config.ini')
    HOST_URL = LOCUST_CFG['DEFAULT']['ENDPOINT_URL']
    HATCH_RATE = int(LOCUST_CFG['DEFAULT']['HATCH_RATE'])
    LOG_FILE = "".join([LOCUST_CFG['DEFAULT']['LOGFILE'],
                        str(time.strftime("-%Y%m%d-%H%M%S")), ".log"])
    HTML_FILE = "".join([LOCUST_CFG['DEFAULT']['HTMLFILE'], str(
        time.strftime("-%Y%m%d-%H%M%S")), ".html"])
    ULIMIT_CMD = "ulimit -n 100000"
    LOCUST_RUN_CMD = \
        "locust --host={} -f {} --headless -u {} -r {} --run-time {} --html {} --logfile {}"
    parser = argparse.ArgumentParser(description='Run locust tool.')
    parser.add_argument('--file_path', help='locust.py file path')
    parser.add_argument('--host', dest='host_url', help='host URL', nargs='?', const=HOST_URL,
                        type=str, default=HOST_URL)
    parser.add_argument(
        '--u', dest='user_count', help='number of Locust users to spawn', nargs='?', type=int)
    parser.add_argument(
        '--r', dest='hatch_rate',
        help='specifies the hatch rate (number of users to spawn per second)',
        nargs='?', const=HATCH_RATE, type=int, default=HATCH_RATE)
    parser.add_argument(
        '--t', dest='duration', help='specify the run time for a test, eg:1h30m',
        nargs='?', type=str)
    parser.add_argument(
        '--logfile', dest='log_file', help='specify the path to store logs', nargs='?',
        const=LOG_FILE, type=str, default=LOG_FILE)
    args = parser.parse_args()
    LOGGER.info("Setting ulimit for locust\n")
    LOCUST_RUN_CMD = LOCUST_RUN_CMD.format(
        args.host_url,
        args.file_path,
        args.user_count,
        args.hatch_rate,
        args.duration,
        HTML_FILE,
        args.log_file)
    env = os.environ.copy()
    if sys.platform == "linux2":
        CMD = "{}; {}\n".format(ULIMIT_CMD, LOCUST_RUN_CMD)
    else:
        CMD = LOCUST_RUN_CMD
    run_local_cmd(CMD, env=env)


if __name__ == '__main__':
    main()
    LOGGER.info("Locust run completed.")
