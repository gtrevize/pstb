import os
import sys
from typing import Generator
from unittest.mock import patch

import pytest
import requests

# Add the src directory to the PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

from pstb.number import (  # noqa: E402 - ignore module level import not at top of file due to sys.path.insert
    pstb_random,
)


class MockQuotaResponse:
    def __init__(self, status_code: int, quota_remaining: int):
        self.status_code = status_code
        self.text = str(quota_remaining)


class MockApiResponse:
    def __init__(self, status_code: int, data: list[int] = []):
        self.status_code = status_code
        self.json_data = {"result": {"random": {"data": data}}}

    def json(self) -> dict:
        return self.json_data


def test_check_random_org_quota_normal():
    with patch("requests.get", return_value=MockQuotaResponse(200, 10000)):
        assert pstb_random.check_random_org_quota(100)


def test_check_random_org_quota_request_exception():
    with patch("requests.get", side_effect=requests.exceptions.RequestException):
        with pytest.raises(requests.exceptions.RequestException):
            pstb_random.check_random_org_quota(100, fail_on_error=True)


def test_check_random_org_quota_timeout():
    with patch("requests.get", side_effect=requests.exceptions.Timeout):
        with pytest.raises(requests.exceptions.Timeout):
            pstb_random.check_random_org_quota(100, timeout=1, fail_on_error=True)


def test_check_random_org_quota_not_enough_quota():
    with patch("requests.get", return_value=MockQuotaResponse(200, 500)):
        with pytest.raises(pstb_random.RandomQuotaExceeded) as excinfo:
            assert not pstb_random.check_random_org_quota(1000, fail_on_error=True)

        assert "Quota exceeded" in str(excinfo.value)


def test_get_true_random_integers_normal():
    with patch("pstb.number.pstb_random.check_random_org_quota", return_value=True):
        result = pstb_random.get_true_random_integers(5, 1, 10)
        assert result is not None
        all_results = list(result)
        assert len(all_results) == 5
        assert all(1 <= num <= 10 for num in all_results)


def test_get_true_random_integers_with_api_key():
    with patch("pstb.number.pstb_random.check_random_org_quota", return_value=True):
        with patch("requests.post", return_value=MockApiResponse(200, data=[1, 2, 3, 4, 5])):
            result = pstb_random.get_true_random_integers(5, 1, 10, api_key="your_api_key")
            assert result is not None
            assert len(result) == 5
            assert all(1 <= num <= 10 for num in result)


def test_get_true_random_integers_without_api_key():
    with patch("pstb.number.pstb_random.check_random_org_quota", return_value=True):
        result = pstb_random.get_true_random_integers(5, 1, 10)
        assert result is not None
        assert len(result) == 5
        assert all(1 <= num <= 10 for num in result)


def test_get_true_random_integers_request_exception():
    with patch(
        "pstb.number.pstb_random.check_random_org_quota",
        side_effect=requests.exceptions.RequestException,
    ):
        with pytest.raises(requests.exceptions.RequestException):
            pstb_random.get_true_random_integers(5, 1, 10, fail_on_error=True)


def test_get_true_random_integers_timeout():
    with patch("pstb.number.pstb_random.check_random_org_quota", side_effect=requests.exceptions.Timeout):
        with pytest.raises(requests.exceptions.Timeout) as excinfo:
            pstb_random.get_true_random_integers(10, 1, 10, timeout=1, fail_on_error=True)

        assert "timed out" in str(excinfo.value)


def test_get_true_random_integers_unique_impossible():
    with patch("pstb.number.pstb_random.check_random_org_quota", return_value=True):
        result = pstb_random.get_true_random_integers(11, 1, 10, unique=True)
        assert result is None


def test_get_true_random_string_normal():
    with patch("pstb.number.pstb_random.check_random_org_quota", return_value=True):
        result = pstb_random.get_true_random_string(10)
        assert result is not None
        assert len(result) == 10
        assert all(char in pstb_random._ALPHANUMERIC_CHARACTERS for char in result)


def test_get_true_random_string_with_valid_characters():
    with patch("pstb.number.pstb_random.check_random_org_quota", return_value=True):
        valid_characters = "abc123"
        result = pstb_random.get_true_random_string(10, valid_characters=valid_characters)
        assert result is not None
        assert len(result) == 10
        assert all(char in valid_characters for char in result)


def test_get_true_random_string_unique():
    with patch("pstb.number.pstb_random.check_random_org_quota", return_value=True):
        result = pstb_random.get_true_random_string(10, unique=True)
        assert result is not None
        assert len(list(result)) == len(set(result))


def test_true_random_choice_list():
    with patch("pstb.number.pstb_random.check_random_org_quota", return_value=True):
        choices = [1, 2, 3, 4, 5]
        result = next(pstb_random.true_random_choice(choices))
        assert result in choices


def test_true_random_choice_dict():
    with patch("pstb.number.pstb_random.check_random_org_quota", return_value=True):
        choices = {"a": 1, "b": 2, "c": 3}
        result = next(pstb_random.true_random_choice(choices))
        assert result in choices.values()


def test_true_random_choice_multiple():
    with patch("pstb.number.pstb_random.check_random_org_quota", return_value=True):
        choices = [1, 2, 3, 4, 5]
        result = pstb_random.true_random_choice(choices, count=3)
        assert result is not None
        assert isinstance(result, Generator)
        for choice in result:
            assert choice in choices


def test_true_random_choice_unique():
    with patch("pstb.number.pstb_random.check_random_org_quota", return_value=True):
        choices = [n + 1 for n in range(10)]
        result = pstb_random.true_random_choice(choices, 10, unique=True, timeout=60)
        assert result is not None
        assert isinstance(result, Generator)
        result_set = set(result)
        assert len(result_set) == len(choices)
        assert all(choice in choices for choice in result_set)


def test_true_random_choice_empty_list():
    with patch("pstb.number.pstb_random.check_random_org_quota", return_value=True):
        choices = []
        with pytest.raises(ValueError) as excinfo:
            _ = next(pstb_random.true_random_choice(choices))

        assert "choices can't be empty" in str(excinfo.value)


def test_true_random_choice_empty_dict():
    with patch("pstb.number.pstb_random.check_random_org_quota", return_value=True):
        choices = {}
        with pytest.raises(ValueError) as excinfo:
            _ = next(pstb_random.true_random_choice(choices))

        assert "choices can't be empty" in str(excinfo.value)
