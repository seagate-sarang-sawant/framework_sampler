# -*- coding: utf-8 -*-
"""
Utility methods of locust test scenarios
"""
import logging
import time
import json
import random
import string
import hashlib
import pytest
from locust import events
from commons.utils import system_utils
from perf import LOCUST_CFG
from commons.rest_client import RestClient
LOGGER = logging.getLogger(__name__)

AUTHOR_CACHE = system_utils.InMemoryDB(1024*1024)


class LocustUtils:
    """
    Locust Utility methods
    """

    def __init__(self):
        self._config = dict()
        self._config["EP_FQDN"] = 'https://fakerestapi.azurewebsites.net'
        self.client = RestClient(self._config)
        self.headers = {'Content-type': 'application/json',
                        'Accept': 'application/json'}

    @staticmethod
    def remove_author(name):
        """Delete checksum from local DB"""
        global AUTHOR_CACHE
        AUTHOR_CACHE.delete(name)

    @staticmethod
    def store_author(name , author):
        """Store checksum in local DB"""
        global AUTHOR_CACHE
        AUTHOR_CACHE.store(name, author)

    @staticmethod
    def pop_one_random():
        """Pop one random object entry from local DB"""
        global AUTHOR_CACHE
        name, object = AUTHOR_CACHE.pop_one()
        if not name:
            return False, False
        return name, object

    @staticmethod
    def total_time(start_time: float) -> float:
        """
        Method to calculate total time for a request to be completed
        :param start_time: Time when request was initialized
        :return: Total time take by request
        """
        return int((time.time() - start_time) * 1000)

    def create_author(self):
        """
        Call type: POST
        Endpoint: /api/v1/Authors
        {
          "id": 0,
          "idBook": 0,
          "firstName": "string",
          "lastName": "string"
        }

        :return:
        """
        endpoint = self._config["EP_FQDN"] + '/api/v1/Authors'
        id = random.randint(1, 1024 * 1024 * 1024)
        idbook = random.randint(1, 1024 * 1024)
        firstname = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        lastname = ''.join(random.choice(string.ascii_lowercase) for i in range(5))
        author_data = dict(id=id, idBook=idbook, firstName=firstname,
                           lastName=lastname)
        start_time = time.time()
        try:
            resp = self.client.rest_call("post", endpoint=endpoint, data=author_data,
                                          headers=self.headers)
        except (BaseException) as error:
            LOGGER.error("create author %s failed: %s", firstname, error)
            events.request_failure.fire(request_type="post", name="create_author",
                                        response_time=self.total_time(start_time),
                                        response_length=1024, exception=error)
        else:
            events.request_success.fire(request_type="post", name="create_author",
                                        response_time=self.total_time(start_time),
                                        response_length=1024)
            self.store_author(firstname, author_data)
            return json.loads(resp.text)

    def update_author(self, name):
        object = AUTHOR_CACHE.lookup(name)
        lastname = ''.join(random.choice(string.ascii_lowercase) for i in range(5))
        author_data = dict(lastName=lastname)
        object.update(author_data)
        endpoint = self._config["EP_FQDN"] + '/api/v1/Authors/' + f"{object['id']}"
        start_time = time.time()
        try:
            resp = self.client.rest_call("put", endpoint=endpoint, data=object,
                                         headers=self.headers)
        except (BaseException) as error:
            LOGGER.error("update author %s failed: %s", object['firstName'], error)
            events.request_failure.fire(request_type="put", name="update_author",
                                        response_time=self.total_time(start_time),
                                        response_length=1024, exception=error)
        else:
            events.request_success.fire(request_type="put", name="update_author",
                                        response_time=self.total_time(start_time),
                                        response_length=1024)
            self.store_author(name, object)
            return json.loads(resp.text)

    def get_author(self, name):
        """
        Get user by the updated username
        :return:
        """
        object = AUTHOR_CACHE.lookup(name)
        endpoint = self._config["EP_FQDN"] + f"/api/v1/Authors/{object['id']}"
        start_time = time.time()
        try:
            resp = self.client.rest_call("get", endpoint=endpoint,
                                          headers=self.headers)
        except (BaseException) as error:
            LOGGER.error("get author %s failed: %s", object['firstName'], error)
            events.request_failure.fire(request_type="get", name="get_author",
                                        response_time=self.total_time(start_time),
                                        response_length=1024, exception=error)
        else:
            events.request_success.fire(request_type="get", name="get_author",
                                        response_time=self.total_time(start_time),
                                        response_length=1024)
            return json.loads(resp.text)

    def delete_author(self, name):
        """
        Get user by the updated username
        :return:
        """
        object = AUTHOR_CACHE.lookup(name)
        endpoint = self._config["EP_FQDN"] + f"/api/v1/Authors/{object['id']}"
        start_time = time.time()
        try:
            resp = self.client.rest_call("delete", endpoint=endpoint,
                                          headers=self.headers)
        except (BaseException) as error:
            LOGGER.error("delete author %s failed: %s", object['firstName'], error)
            events.request_failure.fire(request_type="delete", name="delete_author",
                                        response_time=self.total_time(start_time),
                                        response_length=1024, exception=error)
        else:
            events.request_success.fire(request_type="delete", name="delete_author",
                                        response_time=self.total_time(start_time),
                                        response_length=1024)
            self.remove_author(name)


if __name__ == '__main__':
    lu = LocustUtils()
    author = lu.create_author()
    print(author)
    author = lu.update_author(author['firstName'])
    print(lu.get_author(author['firstName']))
    print(lu.delete_author(author['firstName']))
    print(lu.get_author(author['firstName']))
