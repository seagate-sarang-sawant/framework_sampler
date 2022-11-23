import time
import pytest
from unittest import TestCase
from assertpy import assert_that
from libs.pets import Pets
from config import CMN_CFG


params = {
    'test_data1': ('POST 200', {
        "id": 1,
        "category": {
            "id": 0,
            "name": "dog"
        },
        "name": "sdfdoggie",
        "photoUrls": [
            "string"
        ],
        "tags": [
            {
                "id": 2,
                "name": "string"
            }
        ],
        "status": "available"
    }
                   ),
    'test_data2': ('POST 200', {
        "id": 2,
        "category": {
            "id": 0,
            "name": "dog"
        },
        "name": "ghimurphy",
        "photoUrls": [
            "string"
        ],
        "tags": [
            {
                "id": 3,
                "name": "string"
            }
        ],
        "status": "available"
    }),
}


class TestPets:
    """Test suite for Pets REST API."""

    @pytest.mark.parametrize('exp_data,test_data', list(params.values()), ids=list(params.keys()))
    @pytest.mark.test('test-2')
    def test_pets(self, rest_client, exp_data, test_data):
        """ Create multiple pets.
        Update pet's status and other details (Statuses to be considered: available,
        pending and sold).
        Get pet by status and verify updated status of pet.
        :return:
        """
        client = rest_client
        pets_obj = Pets(client, CMN_CFG)
        pet = test_data
        pet['name'] = pet['name'] + str(time.time())
        resp = pets_obj.create_pet(pet)
        id = resp['id']
        self.log.debug(f"Created pet  with status {pet['status']}")
        # update some parameters of pet
        ud = dict(id=id,photoUrls=['http://123-45678900'],status='sold')
        pet.update(ud)
        resp = pets_obj.update_pet_status(pet)
        self.log.info(f"Updated pet {resp} with status {pet['status']}")
        TestCase().assertDictEqual(resp, pet)
        self.log.debug(f"Updated pet {pet['name']} successfully")
        # get pet by available status
        resp = pets_obj.find_pet_by_status()
        for pitem in resp:
            if 'name' in pitem and pitem['name'] == pet['name']:
                assert_that(pitem['status']).is_equal_to('sold')
                self.log.info(f"Got pet with status {pet['status']}")
                # additional verification could be added or test could be seperated



