import os
import sys
from unittest.mock import patch

import pytest
import requests

# Add the src directory to the PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

from pstb.number import pstb_random  # noqa: E402


class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self.json_data = json_data

    def json(self):
        return self.json_data


def test_check_random_org_quota_normal():
    with patch("requests.post", return_value=MockResponse(200, {"result": {"bitsLeft": 1000}})):
        assert pstb_random.check_random_org_quota(100)


def test_check_random_org_quota_request_exception():
    with patch("requests.post", side_effect=requests.exceptions.RequestException):
        with pytest.raises(requests.exceptions.RequestException):
            pstb_random.check_random_org_quota(100, fail_on_error=True)


def test_check_random_org_quota_timeout():
    with patch("requests.post", side_effect=requests.exceptions.Timeout):
        with pytest.raises(requests.exceptions.Timeout):
            pstb_random.check_random_org_quota(100, timeout=1, fail_on_error=True)


def test_check_random_org_quota_not_enough_quota():
    with patch("requests.post", return_value=MockResponse(200, {"result": {"bitsLeft": 500}})):
        assert not pstb_random.check_random_org_quota(1000)


def test_get_true_random_integers_normal():
    with patch("ezrandom.check_random_org_quota", return_value=True):
        result = pstb_random.get_true_random_integers(5, 1, 10)
        assert len(result) == 5
        assert all(1 <= num <= 10 for num in result)


def test_get_true_random_integers_with_api_key():
    with patch("ezrandom.check_random_org_quota", return_value=True):
        result = pstb_random.get_true_random_integers(5, 1, 10, api_key="your_api_key")
        assert len(result) == 5
        assert all(1 <= num <= 10 for num in result)


def test_get_true_random_integers_without_api_key():
    with patch("ezrandom.check_random_org_quota", return_value=True):
        result = pstb_random.get_true_random_integers(5, 1, 10)
        assert len(result) == 5
        assert all(1 <= num <= 10 for num in result)


def test_get_true_random_integers_request_exception():
    with patch(
        "ezrandom.check_random_org_quota",
        side_effect=requests.exceptions.RequestException,
    ):
        with pytest.raises(requests.exceptions.RequestException):
            pstb_random.get_true_random_integers(5, 1, 10, fail_on_error=True)


def test_get_true_random_integers_timeout():
    with patch("ezrandom.check_random_org_quota", side_effect=requests.exceptions.Timeout):
        with pytest.raises(requests.exceptions.Timeout):
            pstb_random.get_true_random_integers(5, 1, 10, timeout=1, fail_on_error=True)


def test_get_true_random_integers_unique_impossible():
    with patch("ezrandom.check_random_org_quota", return_value=True):
        result = pstb_random.get_true_random_integers(11, 1, 10, unique=True)
        assert result is None
