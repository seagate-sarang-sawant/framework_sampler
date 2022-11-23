# -*- coding: utf-8 -*-

""" REST API Alert operation Library. """
import logging
import time
import json
import requests
from random import Random
from string import Template
from requests.packages.urllib3.exceptions import InsecureRequestWarning

SSL_REQ = "https://"
NON_SSL = "http://"


class RestClient:
    """
        Rest Client implemented with requests
    """

    def __init__(self, config: dict = None):
        """
        This function will initialize this class
        :param config: configuration of setup
        """
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        self.log = logging.getLogger(__name__)
        self._config = config
        self._request = {"get": requests.get, "post": requests.post,
                         "patch": requests.patch, "delete": requests.delete,
                         "put": requests.put}
        if not self._config.get("port"):
            self._base_url = self._config["EP_FQDN"]
        else:
            self._base_url = "{}:{}".format(
                self._config["EP_FQDN"], str(self._config["port"]))
        self.verify_cert = self._config.get("verify_certificate")

    def rest_call(self, request_type, endpoint=None,
                  data=None, headers=None, params=None, json_dict=None,
                  save_json=False):
        """
        This function will request REST methods like GET, POST ,PUT etc.
        :param request_type: get/post/delete/update etc
        :param endpoint: endpoint url
        :param secure_connection: HTTP / HTTPS connection required
        :param data: data required for REST call
        :param headers: headers required for REST call
        :param params: parameters required for REST call
        :param save_json: In case user required to store json file
        :return: response of the request
        """
        # Building final endpoint request url
        self.log.debug("Request URL : %s", self._base_url)
        self.log.debug("Request type : %s", request_type.upper())
        self.log.debug("Request Header : %s", headers)
        self.log.debug("Request Parameters : %s", params)
        self.log.debug("json_dict: %s", json.dumps(json_dict))
        data = json.dumps(data)
        self.log.debug("Data : %s", data)
        if not endpoint:
            endpoint = self._base_url
        # Request a REST call and retries can be added with backoff
        response_object = self._request[request_type](
            endpoint, headers=headers,
            data=data, params=params, verify=False, json=json_dict)
        self.log.debug("Response Object: %s", response_object)
        try:
            self.log.debug("Response JSON: %s", response_object.json())
        except Exception:   # can base http exception raised by request
            self.log.exception("Response Text: %s", response_object.text)

        # Can be used in case of larger response
        if save_json:
            with open(self._json_file_path, 'w+') as json_file:
                json_file.write(json.dumps(response_object.json(), indent=4))

        return response_object

