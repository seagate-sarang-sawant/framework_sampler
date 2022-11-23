import logging
import json
from http import HTTPStatus
from typing import List
from typing import Dict

"""
Create multiple users with array

Update a user's username and other details
	Call type: PUT
	Endpoint: /user/{username}
	Body: {
  "id": 0,
  "username": "string",
  "firstName": "string",
  "lastName": "string",
  "email": "string",
  "password": "string",
  "phone": "string",
  "userStatus": 0
}

Get user by the updated username
	Call type: GET
	Endpoint: /user/{username}
"""


class Users:

    def __init__(self, client, config):
        self.rest_client = client
        self.log = logging.getLogger(__name__)
        self.com_config = config
        self.headers = {'Content-type': 'application/json',
                        'Accept': 'application/json'}

    def create_multiple_users_with_array(self, users_data: List[Dict]):
        """
        Call type: POST
        Endpoint: /user/createWithArray
        Body: [{
            "id": 0,
            "username": "string",
            "firstName": "string",
            "lastName": "string",
            "email": "string",
            "password": "string",
            "phone": "string",
            "userStatus": 0
            }
        ]

        :return:
        """
        #user_data = json.dumps(users_data)
        endpoint = self.com_config.get('target_url') + '/user/createWithArray'
        resp = self.rest_client.rest_call("post", endpoint=endpoint, data=users_data,
                                      headers=self.headers)
        return json.loads(resp.text)

    def update_user(self, user: Dict):
        """
        Update a user's username and other details
        Call type: PUT
        Endpoint: /user/{username}
        Body: {
            "id": 0,
            "username": "string",
            "firstName": "string",
            "lastName": "string",
            "email": "string",
            "password": "string",
            "phone": "string",
            "userStatus": 0
        }

        :param user:
        :return:
        """
        username = user['username']
        endpoint = self.com_config.get('target_url') + f'/user/{username}'
        resp = self.rest_client.rest_call("put", endpoint=endpoint, data=user,
                                      headers=self.headers)
        return json.loads(resp.text)

    def get_user(self, username):
        """
        Get user by the updated username
        :return:
        """
        endpoint = self.com_config.get('target_url') + f'/user/{username}'
        resp = self.rest_client.rest_call("get", endpoint=endpoint,
                                      headers=self.headers)
        return json.loads(resp.text)
