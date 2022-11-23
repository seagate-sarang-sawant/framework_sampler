import time
import pytest
from unittest import TestCase
from http import HTTPStatus
from assertpy import assert_that
from libs.users import Users
from config import CMN_CFG


pytest.mark.usefixtures('rest_client')
class TestUsers:
    """Test suite for users REST API."""

    def setup_method(self):
        """
        Test method level setup.
        """
        self.log.info("ENDED: Method Level setup test data.")

    def teardown_method(self):
        """
        Test method level teardown.
        """
        self.log.info("STARTED: Teardown of test data")
        self.log.info("ENDED: Method Level Teardown test data.")

    @pytest.mark.test('test-1')
    def test_users(self, rest_client):
        """
        Create multiple users with array
        Update a user's username and other details
        Get user by the updated username

        """
        users = CMN_CFG.get('test_1')
        users[0]['username'] = users[0]['username'] + str(time.time())
        users_obj = Users(self.client, CMN_CFG)
        resp = users_obj.create_multiple_users_with_array(users)
        assert resp['code'] == HTTPStatus.OK, resp.message
        self.log.debug(f'Created users response {resp}')
        # get id
        resp = users_obj.get_user(username=users[0]['username'])
        id = resp['id']
        # update some parameters of user1
        ud = dict(id=id,phone='123-45678900',userStatus=1)
        users[0].update(ud)
        resp = users_obj.update_user(users[0])
        assert resp['code'] == HTTPStatus.OK, resp.message
        self.log.debug(f'Updated user {users[0]} successfully')
        resp = users_obj.get_user(username=users[0]['username'])
        self.log.debug(f'get user {resp} details')
        TestCase().assertDictEqual(resp, users[0])
        # can have own implementation of the deep dict compare
