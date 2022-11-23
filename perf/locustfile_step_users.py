# -*- coding: utf-8 -*-

"""
Locust tasks set creating, updating and deleting authors
"""
import os
import configparser
import logging
from locust import LoadTestShape
from locust import events
from locust import HttpUser
from locust import task, constant
from perf import locust_utils
from commons import log

UTILS_OBJ = locust_utils.LocustUtils()
LOGGER = logging.getLogger(__name__)
log.initialize_loghandler(LOGGER, logging.DEBUG)
LOCUST_CFG = configparser.ConfigParser()


class LocustUser(HttpUser):
    """
    Locust user class
    """
    wait_time = constant(1)

    @events.test_start.add_listener
    def on_test_start(**kwargs):
        LOGGER.info("Starting test setup with %s %s", kwargs.get('--u'), kwargs.get('--t'))

    @task(1)
    def create_author(self):
        UTILS_OBJ.create_author()

    @task(2)
    def update_author(self):
        UTILS_OBJ.update_author()

    @task(3)
    def get_author(self):
        UTILS_OBJ.get_author()

    @task(4)
    def delete_author(self):
        UTILS_OBJ.delete_author()

    @events.test_stop.add_listener
    def on_test_stop(**kwargs):
        LOGGER.info("Starting test cleanup.")
        # cache/data cleanup not impl
        LOGGER.info("Log path: %s", kwargs.get('--logfile'))
        LOGGER.info("HTML path: %s", kwargs.get('--html'))


class StepLoadShape(LoadTestShape):
    """
    A step load shape
    Keyword arguments:
        step_time -- Time between steps
        step_load -- User increase amount at each step
        spawn_rate -- Users to stop/start per second at every step
        time_limit -- Time limit in seconds
    """
    import pdb
    pdb.set_trace()
    LOCUST_CFG.read('locust_config.ini')
    step_time = int(os.getenv('STEP_TIME', LOCUST_CFG['DEFAULT']['STEP_TIME']))
    step_load = int(os.getenv('STEP_LOAD', LOCUST_CFG['DEFAULT']['STEP_LOAD']))
    spawn_rate = int(
        os.getenv(
            'SPAWN_RATE',
            LOCUST_CFG['DEFAULT']['HATCH_RATE']))
    time_limit = int(os.getenv('DURATION', 300))
    max_user = int(os.getenv('MAX_USERS', 100))

    def tick(self):
        run_time = self.get_run_time()

        if run_time < self.time_limit:
            total_new_users = self.spawn_rate * self.step_load
            if total_new_users > self.max_user:
                total_new_users = self.max_user
            self.spawn_rate = self.spawn_rate * 2
            return total_new_users, self.spawn_rate * 2
        return None