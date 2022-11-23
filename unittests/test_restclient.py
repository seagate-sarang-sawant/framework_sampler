"""Test Rest Client."""

import logging
import os
from time import perf_counter_ns

from commons.utils import system_utils


class TestRestClient:
    """Test S3 utility library class."""

    def setup_method(self):
        """Pre-requisite will be invoked prior to each test case."""
        self.fpath = os.path.join(self.dpath, f"s3utils-{perf_counter_ns()}")
        if not system_utils.path_exists(self.dpath):
            system_utils.make_dirs(self.dpath)

    def teardown_method(self):
        """Teardown will be invoked after each test case."""
        if system_utils.path_exists(self.dpath):
            system_utils.remove_dirs(self.dpath)

    def test_rest_client_post(self):
        pass

    def test_rest_client_put(self):
        pass

    def test_rest_client_get(self):
        pass