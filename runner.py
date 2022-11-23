#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Test bot or worker which can be integrated with Jira. Could help provide a mechanism to spawn
multiple processes to distribute the parallely runnable tests. Could gets inputs from
Jira Test Plan or Kafka Message. Runs test sequentially or in parallel
and report the results to DB and Jira.
"""
import os
import sys
import subprocess
import argparse
import csv
import logging
from datetime import datetime
from commons import params
from commons import log

LOGGER = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--html_report", type=str, default='report.html',
                        help="html report name")
    parser.add_argument("-pe", "--parallel_exec", type=str, default=False,
                        help="parallel_exec: True for parallel, False for sequential")
    parser.add_argument("-p", "--prc_cnt", type=int, default=2,
                        help="number of parallel processes")
    parser.add_argument("-tg", "--target", type=str,
                        default='https://petstore.swagger.io/', help="AUT URL")
    parser.add_argument("-l", "--log_level", type=int, default=10,
                        help="log level value as defined below" +
                             "CRITICAL = 50" +
                             "FATAL = CRITICAL" +
                             "ERROR = 40" +
                             "WARNING = 30 WARN = WARNING" +
                             "INFO = 20 DEBUG = 10"
                        )
    parser.add_argument("--stop_on_first_error", "-x", dest="stop_on_first_error",
                        action="store_true", help="Stop test execution on first failure")
    parser.add_argument("-s", "--validate_certs", type=str_to_bool, default=True,
                        help="HTTPS/SSL connection without cert validation.")
    return parser.parse_args()


def str_to_bool(val):
    """To convert a string value to bool."""
    if isinstance(val, bool):
        return val
    if val.lower() in ('yes', 'true', 'y', '1'):
        return True
    elif val.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def run_pytest_cmd(args, parallel_exec=False, env=None):
    """Form a pytest command for execution."""
    if parallel_exec:
        raise NotImplementedError()
    env['TARGET'] = args.target
    build, build_type = args.build, args.build_type

    run_type = ''
    log_level = "--log-cli-level=" + str(args.log_level)
    # we intend to use --log-level instead of cli

    report_name = "--html=log/sequential_" + \
        datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S-%f') + args.html_report
    cmd_line = ["pytest", log_level, report_name]

    if args.target:
        cmd_line = cmd_line + ["--target=" + args.target]

    if args.stop_on_first_error:
        cmd_line = cmd_line + ["-x"]

    cmd_line = cmd_line + ['--validate_certs=' + str(args.validate_certs)]
    LOGGER.debug('Running pytest engine %s', cmd_line)
    prc = subprocess.Popen(cmd_line, env=env)
    prc.communicate()
    if prc.returncode == 3:
        print('Exiting test runner due to bad gateway error')
        sys.exit(1)


def trigger_tests(args):
    """
    Trigger tests using pytest
    """
    _env = os.environ.copy()
    # Sequentially execute all tests with parallel tag which are mentioned in given tag.
    run_pytest_cmd(args, True, env=_env)


def main(args):
    """Main Entry function using argument parser to parse options and forming pyttest command.
    """
    trigger_tests(args)


if __name__ == '__main__':
    opts = parse_args()
    level = opts.log_level
    level = logging.getLevelName(level)
    opts.log_level = level
    log.initialize_loghandler(LOGGER, level=level)
    main(opts)
