#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Bucket Location Test Module."""

import logging
import os
from datetime import datetime, timedelta

import pytest

from perf import locust_runner

error_strings = ["InternalError", "Gateway Timeout", "ServiceUnavailable", "ValueError",
                 "bad interpreter", "exceptions", "stderr", "error"]

INPUT_DURATION = "00:10:00"  # HH:MM:SS
duration_t = datetime.strptime(INPUT_DURATION, "%H:%M:%S")
delta = timedelta(hours=duration_t.hour, minutes=duration_t.minute, seconds=duration_t.second)
DURATION_S = int(delta.total_seconds())
DURATION = str(DURATION_S)+"s"


class TestS3Load:
    """ S3 Load Testing suite"""

    @classmethod
    def setup_class(cls):
        """
        Function will be invoked prior to each test case.

        It will perform all prerequisite test suite steps if any.
        """
        cls.log = logging.getLogger(__name__)
        cls.log.info("STARTED: setup test suite operations.")
        cls.account_prefix = "locust-acc"
        cls.email_id = "@seagate.com"
        cls.account_name = None
        os.environ.setdefault("CA_CERT", S3_CFG["s3_cert_path"])
        cls.log.info("account prefix: %s, Bucket prefix:", cls.account_prefix)
        cls.log.info("ENDED: setup test suite operations.")
        cls.locust_file = "scripts/locust/locustfile.py"
        cls.locust_step_user_file = "scripts/locust/locustfile_step_users.py"

    @classmethod
    def teardown_class(cls):
        """
        Function will be invoked after completion of all test case.

        It will clean up resources which are getting created during test suite setup.
        """
        cls.log.info("STARTED: teardown test suite operations.")
        cls.log.info("ENDED: teardown test suite operations.")

    def setup_method(self):
        """
        This function will be invoked prior to each test case.
        It will perform all prerequisite test steps if any.
        Initializing common variable which will be used in test and
        teardown for cleanup
        """
        self.log.info("STARTED: Setup operations.")
        self.host_url = S3_CFG["s3_url"]
        os.environ["USE_SSL"] = "True" if S3_CFG["use_ssl"] else "False"
        os.environ["CA_CERT"] = S3_CFG["s3_cert_path"] if S3_CFG["validate_certs"] else "False"
        os.environ.setdefault("ENDPOINT_URL", self.host_url)
        self.log.info("USE_SSL %s, CA_CERT %s, ENDPOINT_URL %s",
                      os.getenv("USE_SSL"), os.getenv("CA_CERT"), self.host_url)
        self.account_name = self.account_prefix
        os.environ["AWS_ACCESS_KEY_ID"] = ACCESS_KEY
        os.environ["AWS_SECRET_ACCESS_KEY"] = SECRET_KEY
        self.log.info("ENDED: Setup operations.")

    def teardown_method(self):
        """
        This function will be invoked after each test case.
        It will perform all cleanup operations.
        This function will delete buckets and accounts created for tests.
        """
        self.log.info("STARTED: Teardown operations.")
        self.log.info("ENDED: Teardown operations.")

    @staticmethod
    def check_errors(log_file):
        """Check errors in logfile"""
        if os.path.exists(log_file):
            res = locust_runner.check_log_file(log_file, error_strings)
            assert_utils.assert_false(res, "Few IO failed due to some reason")

    @pytest.mark.s3_io_load
    @pytest.mark.tags("TEST-19534")
    def test_small_obj_multi_bkt_max_session_19534(self):
        """
        Load test with multiple buckets, small size objects and max supported concurrent sessions.
        """
        self.log.info("Setting up test configurations")
        os.environ["MAX_POOL_CONNECTIONS"] = str(100)
        os.environ["BUCKET_COUNT"] = str(100)
        os.environ["MIN_OBJECT_SIZE"] = os.environ["MAX_OBJECT_SIZE"] = str(25*Sizes.KB)
        self.log.info("Configurations completed successfully.")
        self.log.info("Starting locust run.")
        res = locust_runner.run_locust(test_id="TEST-19534", host=self.host_url,
                                       locust_file=self.locust_file, users=30, duration=DURATION)
        self.log.info(res)
        self.log.info("Successfully executed locust run.")
        self.log.info("Checking locust log file.")
        log_file = res[1]["log-file"]
        self.check_errors(log_file)
        self.log.info("Validated locust log file.")

    @pytest.mark.s3_io_load
    @pytest.mark.tags("TEST-19537")
    def test_small_obj_increase_session_19537(self):
        """
        Load test with small size objects and gradually increasing users per hr.
        """
        self.log.info("Setting up test configurations")
        os.environ["MAX_POOL_CONNECTIONS"] = str(100)
        os.environ["BUCKET_COUNT"] = str(50)
        os.environ["STEP_TIME"] = str(60)
        os.environ["STEP_LOAD"] = str(50)
        os.environ["SPAWN_RATE"] = str(3)
        os.environ["MIN_OBJECT_SIZE"] = os.environ["MAX_OBJECT_SIZE"] = str(10*Sizes.KB)
        self.log.info("Configurations completed successfully.")
        self.log.info("Starting locust run.")
        res = locust_runner.run_locust(test_id="TEST-19537", host=self.host_url,
                                       locust_file=self.locust_step_user_file,
                                       users=10, duration=DURATION)
        self.log.info(res)
        self.log.info("Successfully executed locust run.")
        self.log.info("Checking locust log file.")
        log_file = res[1]["log-file"]
        self.check_errors(log_file)
        self.log.info("Validated locust log file.")

    @pytest.mark.s3_io_load
    @pytest.mark.tags("TEST-19538")
    def test_small_obj_sudden_spike_session_19538(self):
        """
        Load test with small size objects and sudden spike in users count.
        """
        self.log.info("Setting up test configurations")
        os.environ["MAX_POOL_CONNECTIONS"] = str(100)
        os.environ["BUCKET_COUNT"] = str(10)
        os.environ["STEP_TIME"] = str(1800)
        os.environ["STEP_LOAD"] = str(150)
        os.environ["SPAWN_RATE"] = str(10)
        os.environ["DURATION"] = str(DURATION_S)
        os.environ["MIN_OBJECT_SIZE"] = os.environ["MAX_OBJECT_SIZE"] = str(10*Sizes.KB)
        self.log.info("Configurations completed successfully.")
        self.log.info("Starting locust run.")
        res = locust_runner.run_locust(test_id="TEST-19538", host=self.host_url,
                                       locust_file=self.locust_step_user_file,
                                       users=150, duration=DURATION)
        self.log.info(res)
        self.log.info("Successfully executed locust run.")
        self.log.info("Checking locust log file.")
        log_file = res[1]["log-file"]
        self.check_errors(log_file)
        self.log.info("Validated locust log file.")

