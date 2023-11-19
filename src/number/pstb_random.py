import os
import secrets
import string
import time

import requests
from dotenv import load_dotenv
from typing_extensions import Literal, TypedDict

#############
# Type hints
#############


class IntegerPayloadParams(TypedDict):
    apiKey: str
    n: int
    min: int
    max: int
    replacement: bool


class RandomOrgIntegersPayload(TypedDict):
    jsonrpc: Literal["4.0"]
    method: Literal["generateIntegers"]
    params: IntegerPayloadParams
    id: int


############################
# Load environment variables
############################

load_dotenv()


###########
# Constants
###########

_RANDOM_ORG_API_KEY = str(os.environ.get("_RANDOM_ORG_API_KEY"))
_RANDOM_ORG_QUOTA_URL = "https://www.random.org/quota/?format=plain"
_RANDOM_ORG_URL = "https://www.random.org/cgi-bin/randbyte?nbytes={count}&format=h"
_RANDOM_ORG_API_URL = "https://api.random.org/json-rpc/4/invoke"

# Define the JSON-RPC request payload to get usage
_RANDOM_ORG_QUOTA_PAYLOAD = {
    "jsonrpc": "4.0",
    "method": "getUsage",
    "params": {"apiKey": _RANDOM_ORG_API_KEY},
    "id": 42,
}

# Define the JSON-RPC request payload to generate integers
_RANDOM_ORG_INTEGERS_PAYLOAD: RandomOrgIntegersPayload = {
    "jsonrpc": "4.0",
    "method": "generateIntegers",
    "params": {
        "apiKey": _RANDOM_ORG_API_KEY,
        "n": 0,  # Number of integers to generate. Needs to be replaces before sending the request
        "min": 0,  # Minimum value allowed for each integer. Needs to be replaces before sending the request
        "max": 0,  # Maximum value allowed for each integer. Needs to be replaces before sending the request
        "replacement": False,  # Whether the integers should be unique. False means Not unique, True means unique.
        # Needs to be replaces before sending the request
    },
    "id": 42,
}


######################
# Function definitions
######################


def get_true_random_bytes(
    count: int, timeout: int = 10, fail_on_error: bool = False
) -> bytes:
    """
    Fetches true random bytes from random.org.
    If that fails falls back to pseudo-random numbers using urandom.
    Checks random.org quota before making the request.

    Args:
        count (int): The number of bytes to fetch.
        timeout (int, optional): The timeout for the request to random.org (in seconds). Default is 10 seconds.
        fail_on_error (bool, optional): If True, raise an exception if the request to random.org fails.
            Default is False.

    Returns:
        bytes: The fetched random bytes.

    Raises:
        requests.exceptions.RequestException: If the request to random.org fails and fail_on_error is True.
        requests.exceptions.Timeout: If the request to random.org times out and fail_on_error is True.
    """
    try:
        # Check quota before requesting true random numbers
        if check_random_org_quota(count, timeout=timeout, fail_on_error=fail_on_error):
            # There's enough quota, fetch true random numbers
            random_org_url = _RANDOM_ORG_URL.format(count=count)
            response = requests.get(random_org_url, timeout=timeout)
            if response.status_code == 200:
                return bytes.fromhex(response.text)
            else:
                # If error on request raise Exception or fallback to pseudo-random numbers
                if fail_on_error:
                    raise requests.exceptions.RequestException(
                        f"Request to random.org failed with status code {response.status_code}"
                    )
        else:
            # If quota is not sufficient raise Exception or fallback to pseudo-random numbers
            if fail_on_error:
                raise requests.exceptions.RequestException(
                    f"Quota exceeded trying to generate {count * 8} bits."
                )

    except requests.exceptions.Timeout:
        if fail_on_error:
            raise requests.exceptions.RequestException(
                f"Request to random.org timed out after {timeout} seconds"
            )
    except requests.exceptions.RequestException as e:
        # Handle timeout or other request errors raise Exception or fallback to pseudo-random numbers
        if fail_on_error:
            raise requests.exceptions.RequestException(
                f"Request to random.org failed with exception {e}"
            )

    return os.urandom(count)


def get_random_integers(
    count: int,
    min: int,
    max: int,
    timeout: int = 10,
    api_key: str = _RANDOM_ORG_API_KEY,
    fail_on_error: bool = False,
    unique: bool = False,
):
    """
    Fetches true random integers from random.org.
    Requires an API key, if none is provided, falls back to generating integers from random.org bytes.
    If that fails falls back to pseudo-random numbers using urandom.

    Args:
        count (int): The number of integers to fetch.
        min (int): The smallest value allowed for each integer.
        max (int): The largest value allowed for each integer.
        timeout (int, optional): The timeout for the function to complete. If has to main uses:
            1) As a timeout for the request to random.org (in seconds).
            2) As a timeout for the function to complete (in seconds). This is used to ensure that the function
            does not run for too long, especially when generating unique random integers.
            Default is 10 seconds.
        api_key (str, optional): The API key to use for the request. If None, the value of the _RANDOM_ORG_API_KEY
            environment variable will be used. Default is None.
        fail_on_error (bool, optional): If True, raise an exception if the request to random.org fails.
            Default is False.
        unique (bool, optional): If True, the fetched integers will be unique within this call. Default is False.

    Returns:
        list: The fetched random integers.
        None: If unique is True and and fail_on_error is False and it is not possible to
            generate unique random integers given the range.

    Raises:
        requests.exceptions.RequestException: If the request to random.org fails and fail_on_error is True.
        requests.exceptions.Timeout: If the request to random.org times out and fail_on_error is True.
    """

    # Check arguments sanity
    if min > max:
        if fail_on_error:
            raise ValueError(
                "Minimum value must be less than or equal to the maximum value"
            )
        else:
            return None

    if (max - min + 1) < count:
        if fail_on_error:
            raise ValueError(
                f"It is not possible to generate unique {count} random integers given the range {min}-{max}"
            )
        else:
            return None

    try:
        # Check quota before requesting true random numbers
        if check_random_org_quota(
            count, timeout=timeout, api_key=api_key, fail_on_error=fail_on_error
        ):
            if api_key:
                # Populate the JSON-RPC integers request payload
                random_org_integers_payload = _RANDOM_ORG_INTEGERS_PAYLOAD.copy()
                random_org_integers_payload["params"]["n"] = count
                random_org_integers_payload["params"]["min"] = min
                random_org_integers_payload["params"]["max"] = max
                random_org_integers_payload["params"]["replacement"] = not unique

                # Make the POST request to the API
                response = requests.post(
                    _RANDOM_ORG_API_URL,
                    json=_RANDOM_ORG_INTEGERS_PAYLOAD,
                    timeout=timeout,
                )
                if response.status_code == 200:
                    # Parse the JSON response
                    data = response.json()
                    # Extract the random integers from the response
                    if "result" in data and "random" in data["result"]:
                        random_integers = data["result"]["random"]["data"]
                        return random_integers
                    else:
                        # If quota is not sufficient raise Exception or fallback to pseudo-random numbers
                        if fail_on_error:
                            raise requests.exceptions.RequestException(
                                "Warning not enough quota in random.org"
                            )
                else:
                    # If error on request raise Exception or fallback to pseudo-random numbers
                    if fail_on_error:
                        raise requests.exceptions.RequestException(
                            f"Request to random.org failed with status code {response.status_code}"
                        )
            else:
                # There's enough quota, fetch true random numbers without an API key
                random_org_url = _RANDOM_ORG_URL.format(count=count)
                response = requests.get(random_org_url, timeout=timeout)
                if response.status_code == 200:
                    return [
                        int(byte) % (max - min + 1) + min
                        for byte in bytes.fromhex(response.text)
                    ]
                else:
                    # If error on request raise Exception or fallback to pseudo-random numbers
                    if fail_on_error:
                        raise requests.exceptions.RequestException(
                            f"Request to random.org failed with status code {response.status_code}"
                        )
        else:
            # If quota is not sufficient raise Exception or fallback to pseudo-random numbers
            if fail_on_error:
                raise requests.exceptions.RequestException(
                    f"Quota exceeded trying to generate {count} integers."
                )

    except requests.exceptions.Timeout:
        if fail_on_error:
            raise requests.exceptions.RequestException(
                f"Request to random.org timed out after {timeout} seconds"
            )

    except requests.exceptions.RequestException as e:
        # Handle timeout or other request errors raise Exception or fallback to pseudo-random numbers
        if fail_on_error:
            raise requests.exceptions.RequestException(
                f"Request to random.org failed with exception {e}"
            )

    # Fallback to pseudo-random numbers using secrets module
    if not unique:
        return [min + secrets.randbelow(max - min + 1) for _ in range(count)]
    else:
        start_time = time.perf_counter()
        generated_numbers: set[int] = set()
        while len(generated_numbers) < count:
            elapsed_time = (
                time.perf_counter() - start_time
            ) * 1000  # Convert to milliseconds
            if timeout is not None and elapsed_time > (
                timeout * 1000
            ):  # Convert timeout to milliseconds
                raise ValueError(
                    f"Timeout: {timeout} secs; generating {count} unique random integers within the range {min}-{max}"
                )
            if unique:
                generated_numbers.add(min + secrets.randbelow(max - min + 1))
            else:
                return [min + secrets.randbelow(max - min + 1) for _ in range(count)]


def generate_random_integers(count, min_value, max_value):
    byte_data = get_true_random_bytes(count)
    return [int(byte) % (max_value - min_value + 1) + min_value for byte in byte_data]


def generate_random_string(length):
    """
    Generates a random string of alphanumeric characters.

    Args:
        length (int): The length of the random string to generate.

    Returns:
        str: The generated random string.

    Raises:
        ValueError: If length is less than 1.
    """

    if length < 1:
        raise ValueError("length must be greater than 0")

    characters = string.ascii_letters + string.digits
    numbers = get_true_random_bytes(length)
    return "".join(os.urandom.choice(characters) for _ in range(length))


def check_random_org_quota(
    count, timeout=10, api_key=_RANDOM_ORG_API_KEY, fail_on_error=False
):
    """
    Checks if there is enough quota left on random.org.

    Args:
        count (int): The number of bytes to fetch.
        timeout (int, optional): The timeout for the request to random.org (in seconds). Default is 10 seconds.
        api_key (str, optional): The API key to use for the request. If None, the value of the _RANDOM_ORG_API_KEY.
        fail_on_error (bool, optional): If True, raise an exception if the request to random.org fails.
            Default is False.

    Returns:
        boolean: True if there is enough quota left, False otherwise.

    Raises:
        requests.exceptions.RequestException: If the request to random.org fails and fail_on_error is True.
        requests.exceptions.Timeout: If the request to random.org times out and fail_on_error is True.
    """

    try:
        if api_key:
            # Check quota with an API key
            response = requests.post(
                _RANDOM_ORG_API_URL, json=_RANDOM_ORG_QUOTA_PAYLOAD, timeout=timeout
            )
            if response.status_code == 200:
                remaining = response.json()["result"]["bitsLeft"]
                if remaining >= count * 8:
                    return True
                else:
                    return False
            else:
                # If error on request raise Exception or fallback to pseudo-random numbers
                if fail_on_error:
                    raise requests.exceptions.RequestException(
                        f"Request to random.org failed with status code {response.status_code}"
                    )
        else:
            # Check quota without an API key. It uses the requesting IP address.
            response = requests.get(_RANDOM_ORG_QUOTA_URL, timeout=timeout)

            if response.status_code == 200:
                # Response is in bits, convert to bytes. Assume 8 bits per byte.
                quota = int(response.text.strip()) / 8
                if quota >= count:
                    return True
                else:
                    return False
            else:
                # If error on request raise Exception or fallback to pseudo-random numbers
                if fail_on_error:
                    raise requests.exceptions.RequestException(
                        f"Request to random.org failed with status code {response.status_code}"
                    )

    except requests.exceptions.Timeout:
        if fail_on_error:
            raise requests.exceptions.RequestException(
                f"Request to random.org timed out after {timeout} seconds"
            )
        else:
            return False

    except requests.exceptions.RequestException as e:
        # Handle timeout or other request errors raise Exception or fallback to pseudo-random numbers
        if fail_on_error:
            raise requests.exceptions.RequestException(
                f"Request to random.org failed with exception {e}"
            )
        else:
            return False


def main():
    pass


if __name__ == "__main__":
    main()
