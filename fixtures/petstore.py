import logging
import pytest
from commons.rest_client import RestClient
from config import CMN_CFG


@pytest.fixture(scope="class", autouse=False)
def rest_client(request):
    """
    Yield fixture to setup pre requisites and teardown them.
    Part before yield will be invoked prior to each test case and
    part after yield will be invoked after test call i.e as teardown.
    """
    target_url = CMN_CFG['target_url']
    request.cls.log = logging.getLogger(__name__)
    request.cls.log.info("STARTED: Setup test operations.")
    request.cls._config = dict()
    request.cls._config["EP_FQDN"] = target_url
    request.cls.client = RestClient(request.cls._config)
    request.cls.log.info("ENDED: Setup test suite operations.")
    yield request.cls.client
    request.cls.log.info("STARTED: Test suite Teardown operations")
    del request.cls.client
    request.cls.log.info("ENDED: Test suite Teardown operations")

