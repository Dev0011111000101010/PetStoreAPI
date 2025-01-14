import json

import allure
import pytest
import requests


from src.assertions import Assertions
from src.http_methods import MyRequests
from data.data_pet import get_pet_by_status
from data.status_code import StatusCode
from data.urls import PetUrls, BASE_URL
from tests.test_vera.data.data_pets import expected_pet_keys
from tests.test_vera.fixtures import headers, pet_data_set


class TestPet:
    status_code = StatusCode()
    link = PetUrls

    @allure.title("Find pets by status > Status code is 200")
    @pytest.mark.parametrize("status", get_pet_by_status)
    def test_01_01_get_pet_by_status_has_status_code_200(self, status):
        """
        This test checks availability of pets by status
        and checks the status code of the response
        :param for status: "available", "pending",  "sold"
        """
        response = MyRequests.get(self.link.BY_STATUS, status)
        Assertions.assert_code_status(response, self.status_code.STATUS_CODE_200)

    @allure.title("Find pets by status > Expected number of pets for each status")
    @pytest.mark.parametrize("status", get_pet_by_status)
    def test_pets_count_by_status(self, status):
        """
        The test checks if the response contains the expected number of pets for each status
        :param for status: "available", "pending",  "sold"
        """
        response = MyRequests.get(self.link.BY_STATUS, data=status)
        data = response.json()
        assert isinstance(data, list)
        assert all(pet['status'] == status['status'] for pet in data)

    @allure.title("Find pets by status > Response content type is JSON")
    @pytest.mark.parametrize("status", get_pet_by_status)
    def test_response_content_type(self, status):
        """ The test checks if the response content type is JSON """
        response = MyRequests.get(self.link.BY_STATUS, data=status)
        Assertions.assert_response_has_be_json(response)


    @allure.title("Find pets by status > Response headers contain the necessary fields")
    @pytest.mark.parametrize("status", get_pet_by_status)
    def test_response_headers(self, status):
        """ The test checks if the response cheaders contain the necessary fields"""
        get_pet_by_status_headers = ['access-control-allow-headers', 'access-control-allow-methods',
                                     'access-control-allow-origin',
                                     'content-type', 'content-type', 'date', 'server']
        response = MyRequests.get(self.link.BY_STATUS, data=status)
        for header, value in response.headers.items():
            print(f"{status} - {header}: {value}")
            if header in get_pet_by_status_headers:
                assert header in response.headers, f"Expected header '{header}' not found"
                assert value == get_pet_by_status_headers[
                    header], f"Expected value '{get_pet_by_status_headers[header]}' for header '{header}'"


class TestCreatePet:
    status_code = StatusCode()
    link = PetUrls

    @allure.title("Create pet > Status code is 200")
    def test_add_pet_to_store(self, headers, pet_data_set):
        url = BASE_URL+self.link.PET
        response = requests.post(url, json=pet_data_set, headers=headers)
        Assertions.assert_code_status(response, self.status_code.STATUS_CODE_200)

    @allure.title("Create pet > Response is in json format")
    def test_add_pet_response_format(self, headers, pet_data_set):
        """ The test checks response is in json format for the created pet """
        url = BASE_URL+self.link.PET
        json_data = json.dumps(pet_data_set) # Serialize the data dictionary to JSON
        # response = MyRequests.post(url, data=json_data, headers=headers)
        response = requests.post(url, data=json_data, headers=headers)
        Assertions.assert_response_has_be_json(response)

    @allure.title("Create pet > Expected pet 'id' in response")
    def test_add_pet_id_in_response(self, headers, pet_data_set):
        """ The test checks "id" in json response for the created pet """
        url = BASE_URL+self.link.PET
        json_data = json.dumps(pet_data_set)  # Serialize the data dictionary to JSON
        # response = MyRequests.post(url, data=json_data, headers=headers)
        response = requests.post(url, data=json_data, headers=headers)
        try:
            json_response = response.json()
            print(json_response)
            assert "id" in json_response, "Failed to find 'id' in the JSON response"
            assert json_response["id"] != 0, "'id' in the JSON response is 0"
            print(json_response["id"])
        except json.JSONDecodeError:
            print(response.content.decode())
            assert False, "Failed to decode response JSON"

    @allure.title("Create pet > Expected pet keys in response")
    def test_add_pet_keys_in_response(self, headers, pet_data_set):
        """ The test checks "id" in json response for the created pet """
        url = BASE_URL+self.link.PET
        json_data = json.dumps(pet_data_set)  # Serialize the data dictionary to JSON
        # response = MyRequests.post(url, data=json_data, headers=headers)
        response = requests.post(url, data=json_data, headers=headers)
        Assertions.assert_response_has_be_json(response)
        for key in expected_pet_keys:
            assert key in response.json(), f"Missing key '{key}' in the JSON response"

    @allure.title("Create pet > Expected pet name in response")
    def test_add_pet_name_in_response(self, headers, pet_data_set):
        """ The test checks pet's name in json response for the created pet """
        json_data = json.dumps(pet_data_set)  # Serialize the data dictionary to JSON
        # response = MyRequests.post(BASE_URL+self.link.PET, data=json_data, headers=headers)
        response = requests.post(BASE_URL+self.link.PET, data=json_data, headers=headers)
        Assertions.assert_response_has_be_json(response)
        Assertions.assert_json_value_by_name(response, 'name', pet_data_set['name'],
                                             "Incorrect pet name in the response")

class TestUpdatePet:
    status_code = StatusCode()
    link = PetUrls

    @allure.title("Update pet > Status code is 200")
    def test_update_pet_success(self, pet_data_set):
        """
        The test updates pet's information with valid data
        and checks the status code of the response
        """
        pet_data_set["name"] = "new name"
        response = requests.put(BASE_URL + self.link.PET, json=pet_data_set)
        print(response.json())
        Assertions.assert_code_status(response, self.status_code.STATUS_CODE_200)
        Assertions.assert_json_value_by_name(response, "name", "new name", "Failed to update the pet's name")

    @allure.title("Update pet > Name is updated")
    def test_update_pet_success(self, pet_data_set):
        """
        Test updates the pet's name and checks if it is updated successfully.
        """
        pet_data_set["name"] = "new name"
        response = requests.put(BASE_URL + self.link.PET, json=pet_data_set)
        print(response.json())
        Assertions.assert_code_status(response, self.status_code.STATUS_CODE_200)
        Assertions.assert_json_value_by_name(response, "name", "new name", "Failed to update the pet's name")
