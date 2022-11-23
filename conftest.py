# -*- coding: utf-8 -*-

"""This file is core of the framework and it contains common Pytest fixtures and hooks."""
import ast
import datetime
import logging
import os
import random
import string
import time
import xml.etree.ElementTree as ET

import pytest
from _pytest.main import Session
from strip_ansi import strip_ansi

from config import CMN_CFG
from commons import Globals
from commons import params
from commons.utils import config_utils
from commons.utils import system_utils
from commons.rest_client import RestClient
from commons.utils.system_utils import LRUCache

from fixtures.petstore import rest_client

FAILURES_FILE = "failures.txt"
LOG_DIR = 'log'
LOGGER = logging.getLogger(__name__)

SKIP_MARKS = ("dataprovider", "test", "run", "skip", "usefixtures",
              "filterwarnings", "skipif", "xfail", "parametrize",
              "tags")

SKIP_DEBUG_LOGS = []  # Disable debug logs for chatty TP packages


def _get_items_from_cache():
    """Intended for internal use after modifying collected items."""
    return CACHE.table


def pytest_addoption(parser):
    """
    Hook to add options at runtime to pytest command
    :param parser:
    :return:
    """
    parser.addoption(
        "--is_parallel", action="store", default=False, help="option: True or False"
    )
    parser.addoption(
        "--local", action="store", default=True, help="Decide whether run is dev local"
    )
    parser.addoption(
        "--target", action="store", default="automation", help="Target or setup under test"
    )
    parser.addoption(
        "--validate_certs", action="store", default=False,
        help="Decide whether to Validate HTTPS/SSL certificate to S3 endpoint."
    )



@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Remove handlers from all loggers."""
    loggers = [logging.getLogger()] + list(logging.Logger.manager.loggerDict.values())
    for _logger in loggers:
        handlers = getattr(_logger, 'handlers', [])
        for handler in handlers:
            _logger.removeHandler(handler)

    try:
        resp = system_utils.umount_dir(mnt_dir=params.MOUNT_DIR)
        if resp[0]:
            print("Successfully unmounted directory")
    except Exception as fault:
        LOGGER.exception(fault)
    filter_report_session_finish(session)


def pytest_sessionstart(session: Session) -> None:
    """Called after the ``Session`` object has been created and before performing collection
    and entering the run test loop.

    :param pytest.Session session: The pytest session object.
    """
    # db_user, db_passwd = CMN_CFG.db_user, CMN_CFG.db_passwd
    # init_instance db_user=None, db_passwd=None
    reset_imported_module_log_level(session)


def reset_imported_module_log_level(session):
    """Reset logging level of imported modules.
    Add check for imported module logger.
    """
    log_level = session.config.option.log_cli_level
    if not log_level:
        log_level = logging.DEBUG  # default=10 for pytest direct invocation without log cli level
    loggers = [logging.getLogger()] + list(logging.Logger.manager.loggerDict.values())
    for _logger in loggers:
        # Handle Place holders logging
        if isinstance(_logger, logging.PlaceHolder):
            LOGGER.debug("Skipping placeholder to reset logging level")
            continue

    for pkg in SKIP_DEBUG_LOGS:
        logging.getLogger(pkg).setLevel(logging.WARNING)


@pytest.hookimpl(tryfirst=True)
def pytest_collection(session):
    """Collect tests in master and filter out test from TE ticket."""
    items = session.perform_collect()
    config = session.config
    _local = ast.literal_eval(str(config.option.local))
    required_tests = list()
    global CACHE
    CACHE = LRUCache(1024 * 10)
    Globals.LOCAL_RUN = _local
    Globals.TARGET = config.option.target
    if _local:
        meta = list()
        for item in items:
            test_id = ''
            _marks = list()
            for mark in item.iter_markers():
                if mark.name == 'tags':
                    test_id = mark.args[0]
                else:
                    _marks.append(mark.name)
            CACHE.store(item.nodeid, test_id)
            meta.append(dict(nodeid=item.nodeid, test_id=test_id, marks=_marks))
    cache_home = os.path.join(os.getcwd(), params.LOG_DIR_NAME)
    cache_path = os.path.join(cache_home, 'suites.json')
    if not os.path.exists(cache_home):
        try:
            system_utils.make_dir(cache_home)
        except OSError as error:
            LOGGER.error(str(error))
    latest = os.path.join(cache_home, 'latest')
    if not os.path.exists(latest):
        os.makedirs(latest)
    _path = config_utils.create_content_json(cache_path, _get_items_from_cache(), ensure_ascii=False)
    if not os.path.exists(_path):
        LOGGER.info("Items Cache file %s not created" % (_path,))
    return items

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Execute all other hooks to obtain the report object. Follow the pytest execution protocol
    to understand where does this function fits in. In short this function will help to create
    failed, passed lists in multiple runs. The clean up of logs files should happen before the
    test runs starts.
    All code prior to yield statement would be ran prior
    to any other of the same fixtures defined
    :param item:
    :param call:
    :return:
    """
    outcome = yield
    report = outcome.get_result()
    Globals.ALL_RESULT = report
    setattr(item, "rep_" + report.when, report)
    try:
        attr = getattr(item, 'call_duration')
        LOGGER.info('Setting attribute call_duration')
    except AttributeError as attr_error:
        LOGGER.warning('Exception %s occurred', str(attr_error))
        setattr(item, "call_duration", call.duration)
    else:
        setattr(item, "call_duration", call.duration + attr)

    _local = bool(item.config.option.local)
    Globals.LOCAL_RUN = _local
    fail_file = 'failed_tests.log'
    pass_file = 'passed_tests.log'
    current_file = 'other_test_calls.log'
    test_id = CACHE.lookup(report.nodeid)
    if not _local:
        if report.when == 'teardown':
            mode = "a"  # defaults
            current_file = os.path.join(os.getcwd(), LOG_DIR, 'latest', current_file)
            if item.rep_setup.failed or item.rep_teardown.failed:
                current_file = fail_file
                current_file = os.path.join(os.getcwd(), LOG_DIR, 'latest', current_file)
                mode = "a" if os.path.exists(current_file) else "w"
            elif item.rep_setup.passed and (item.rep_call.failed or item.rep_teardown.failed):
                current_file = fail_file
                current_file = os.path.join(os.getcwd(), LOG_DIR, 'latest', current_file)
                mode = "a" if os.path.exists(current_file) else "w"
            elif item.rep_setup.passed and item.rep_call.passed and item.rep_teardown.passed:
                current_file = pass_file
                current_file = os.path.join(os.getcwd(), LOG_DIR, 'latest', current_file)
                mode = "a" if os.path.exists(current_file) else "w"
            elif item.rep_setup.skipped and (item.rep_teardown.skipped or item.rep_teardown.passed):
                current_file = os.path.join(os.getcwd(), LOG_DIR, 'latest', current_file)
                mode = "a" if os.path.exists(current_file) else "w"
            elif item.rep_setup.skipped or item.rep_call.skipped or item.rep_teardown.skipped:
                current_file = os.path.join(os.getcwd(), LOG_DIR, 'latest', current_file)
                mode = "a" if os.path.exists(current_file) else "w"
            with open(current_file, mode) as f:
                if "tmpdir" in item.fixturenames:
                    extra = " ({})".format(item.funcargs["tmpdir"])
                else:
                    extra = ""
                f.write(report.nodeid + extra + "\n")


def pytest_runtest_logreport(report: "TestReport") -> None:
    """
    Provides an intercept to create a) generate log per test case
    :param report:
    :return:
    """
    if Globals.LOCAL_RUN:
        if report.when == 'teardown':
            log = report.caplog
            log = strip_ansi(log)
            logs = log.split('\n')
            test_id = CACHE.lookup(report.nodeid)
            name = str(test_id) + '_' + report.nodeid.split('::')[1] + '_' \
                   + datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S') \
                   + '.log'
            test_log = os.path.join(os.getcwd(), LOG_DIR, 'latest', name)
            with open(test_log, 'w') as fp:
                for rec in logs:
                    fp.write(rec + '\n')
        return
    test_id = CACHE.lookup(report.nodeid)
    if report.when == 'setup' and report.outcome == 'passed':
        # If you reach here and when you know setup passed.
        LOGGER.info("Test setup has passed")
    elif report.when == 'call':
        pass
    elif report.when == 'teardown':
        log = report.caplog
        log = strip_ansi(log)
        logs = log.split('\n')
        test_id = CACHE.lookup(report.nodeid)
        name = str(test_id) + '_' + report.nodeid.split('::')[1] + '_' + \
               datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S') + \
               '.log'
        test_log = os.path.join(os.getcwd(), LOG_DIR, 'latest', name)
        with open(test_log, 'w') as fp:
            for rec in logs:
                fp.write(rec + '\n')
        LOGGER.info("Logs can be uploaded to common location")


def filter_report_session_finish(session):
    if session.config.option.xmlpath:
        path = session.config.option.xmlpath
        tree = ET.parse(path)
        root = tree.getroot()
        with open(path, "w", encoding="utf-8") as logfile:
            logfile.write('<?xml version="1.0" encoding="UTF-8"?>')
            root[0].attrib["package"] = "root"
            for element in root[0]:
                element.attrib["classname"] = element.attrib[
                    "classname"].split(".")[-1]

            logfile.write(ET.tostring(root[0], encoding="unicode"))


@pytest.fixture(scope='function')
def generate_random_string():
    return ''.join(random.choice(string.ascii_lowercase) for i in range(10))

