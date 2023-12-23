"""
This module provides functions to generate random numbers and strings.
It uses random.org as a source of true random numbers.
If that fails, it falls back to pseudo-random numbers using urandom.

Note:
    True random numbers generators (TRNG) is a complex topic, and the subject of significant debate.
    It can have significant implications in security, privacy, etc.
    You should understand the differences and caveats between TRNG, PRNG, and CSPRNG before using them.
    Here is an archived URL of a good discussion on the topic: https://perma.cc/CZK7-EVR4

Functions:
    check_random_org_quota(count: int, timeout: int = 10, api_key: str = _RANDOM_ORG_API_KEY,
    fail_on_error: bool = False) -> None

    get_random_org_quota(count: int, timeout: int = 10, api_key: str = _RANDOM_ORG_API_KEY,
    fail_on_error: bool = False) -> None

    get_true_random_bytes(count: int, timeout: int = 10, fail_on_error: bool = False) -> bytes

    get_true_random_integers(count: int, min: int, max: int, timeout: int = 10, api_key: str = _RANDOM_ORG_API_KEY,
    fail_on_error: bool = False, unique: bool = False) -> List[int]

    generate_random_integers(count: int, min_value: int, max_value: int, timeout: int = 10,
    api_key: str = _RANDOM_ORG_API_KEY, fail_on_error: bool = False) -> List[int]

    generate_random_string(length: int, valid_characters: str = _ALPHANUMERIC_CHARACTERS, unique: bool = False) -> str

    check_random_org_quota(count: int, timeout: int = 10, api_key: str = _RANDOM_ORG_API_KEY,
    fail_on_error: bool = False) -> None

    true_random_choice(choices_set: Set[Any], count: int = 1, unique: bool = False, timeout: int = 10,
    api_key: str = _RANDOM_ORG_API_KEY) -> Union[Any, List[Any]]
"""

import argparse
import json
import os
import secrets
import string
import sys
import time
from typing import Any, Generator

import requests
from dotenv import load_dotenv
from typing_extensions import Literal, TypedDict

#############
# Type hints
#############


class IntegerPayloadParams(TypedDict):
    """Type hint for the params field of the JSON-RPC request payload to generate integers"""

    apiKey: str
    n: int
    min: int
    max: int
    replacement: bool


class QuotaPayloadParams(TypedDict):
    """Type hint for the params field of the JSON-RPC request to check the quota"""

    apiKey: str


class RandomOrgIntegersPayload(TypedDict):
    """Type hint for the JSON-RPC request payload to generate integers"""

    jsonrpc: Literal["4.0"]
    method: Literal["generateIntegers"]
    params: IntegerPayloadParams
    id: int


class RandomOrgQuotaPayload(TypedDict):
    """Type hint for the JSON-RPC request payload to retrieve the quota"""

    jsonrpc: Literal["4.0"]
    method: Literal["getUsage"]
    params: QuotaPayloadParams
    id: int


############
# Exceptions
############


class RandomQuotaExceeded(Exception):
    """
    Exception raised when the quota is exceeded
    """

    def __init__(self, message: str = "Quota exceeded", requested_bits: int = 0, remaining_bits: int = -1) -> None:
        """
        Constructor for the RandomQuotaExceeded exception

        Args:
            message (str, optional): The error message. Default is "Quota exceeded".
            requested_bits (int, optional): The number of bits requested. Default is 0.
            remaining_bits (int, optional): The number of remaining bits. Default is 0.
        """

        self.requested_bytes = int(requested_bits / 8)  # Convert to bytes
        self.remaining_bytes = int(remaining_bits / 8)  # Convert to bytes

        if self.requested_bytes > 0:
            message += f" trying to generate {self.requested_bytes} bytes"

        if self.remaining_bytes != -1:
            message += f" with only {self.remaining_bytes} bytes remaining"

        self.message = message
        super().__init__(self.message)


############################
# Load environment variables
############################

load_dotenv()


###########
# Constants
###########

_RANDOM_ORG_API_KEY: str = os.environ.get("_RANDOM_ORG_API_KEY", "")
_RANDOM_ORG_QUOTA_URL: str = "https://www.random.org/quota/?format=plain"
_RANDOM_ORG_URL: str = "https://www.random.org/cgi-bin/randbyte?nbytes={count}&format=h"
_RANDOM_ORG_API_URL: str = "https://api.random.org/json-rpc/4/invoke"

# Define the JSON-RPC request payload to get usage
_RANDOM_ORG_QUOTA_PAYLOAD: RandomOrgQuotaPayload = {
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

# Define the default valid characters for the random string generator
_ALPHANUMERIC_CHARACTERS: str = string.ascii_letters + string.digits

# Define the maximum length of the random string generator
_MAX_STRING_LENGTH: int = 1000

######################
# Function definitions
######################


def get_true_random_bytes(count: int, timeout: int = 10, fail_on_error: bool = False) -> bytes:
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
                raise requests.exceptions.RequestException(f"Quota exceeded trying to generate {count * 8} bits.")

    except requests.exceptions.Timeout:
        if fail_on_error:
            raise requests.exceptions.RequestException(f"Request to random.org timed out after {timeout} seconds")
    except requests.exceptions.RequestException as e:
        # Handle timeout or other request errors raise Exception or fallback to pseudo-random numbers
        if fail_on_error:
            raise requests.exceptions.RequestException(f"Request to random.org failed with exception {e}")

    return os.urandom(count)


def get_true_random_integers(
    count: int,
    min: int,
    max: int,
    timeout: int = 10,
    api_key: str = _RANDOM_ORG_API_KEY,
    fail_on_error: bool = False,
    unique: bool = False,
) -> list[int] | None:
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
            raise ValueError("Minimum value must be less than or equal to the maximum value")
        else:
            return None

    if unique and ((max - min + 1) < count):
        if fail_on_error:
            raise ValueError(
                f"It is not possible to generate unique {count} random integers given the range {min}-{max}"
            )
        else:
            return None

    generated_numbers: set[int] = set()
    try:
        # Check quota before requesting true random numbers
        if check_random_org_quota(count, timeout=timeout, api_key=api_key, fail_on_error=fail_on_error):
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
                            raise requests.exceptions.RequestException("Warning not enough quota in random.org")
                        else:
                            return None
                else:
                    # If error on request raise Exception or fallback to pseudo-random numbers
                    if fail_on_error:
                        raise requests.exceptions.RequestException(
                            f"Request to random.org failed with status code {response.status_code}"
                        )
                    else:
                        return None
            else:
                # There's enough quota, fetch true random numbers without an API key
                random_org_url = _RANDOM_ORG_URL.format(count=count)
                start_time = time.perf_counter()
                while len(generated_numbers) < count:
                    elapsed_time = (time.perf_counter() - start_time) * 1000  # Convert to milliseconds
                    if timeout is not None and elapsed_time > (timeout * 1000):  # Convert timeout to milliseconds
                        if fail_on_error:
                            raise ValueError(
                                f"""
                                Timeout: {timeout} secs; generating {count} unique random integers
                                within the range {min}-{max}
                                """
                            )
                        else:
                            return None

                    response = requests.get(random_org_url, timeout=timeout)
                    if response.status_code == 200:
                        if unique:
                            generated_numbers.update(
                                [int(byte) % (max - min + 1) + min for byte in bytes.fromhex(response.text)]
                            )
                        else:
                            return [int(byte) % (max - min + 1) + min for byte in bytes.fromhex(response.text)]
                    else:
                        # If error on request raise Exception or fallback to pseudo-random numbers
                        if fail_on_error:
                            raise requests.exceptions.RequestException(
                                f"Request to random.org failed with status code {response.status_code}"
                            )
                        else:
                            return None

                return list(generated_numbers)

    except requests.exceptions.Timeout:
        if fail_on_error:
            raise requests.exceptions.Timeout(f"Request to random.org timed out after {timeout} seconds")
        else:
            return None

    except requests.exceptions.RequestException as e:
        # Handle timeout or other request errors raise Exception or fallback to pseudo-random numbers
        if fail_on_error:
            raise requests.exceptions.RequestException(f"Request to random.org failed with exception {e}")
        else:
            return None

    # Fallback to pseudo-random numbers using secrets module
    if not unique:
        return [min + secrets.randbelow(max - min + 1) for _ in range(count)]
    else:
        start_time = time.perf_counter()
        while len(generated_numbers) < count:
            elapsed_time = (time.perf_counter() - start_time) * 1000  # Convert to milliseconds
            if timeout is not None and elapsed_time > (timeout * 1000):  # Convert timeout to milliseconds
                if fail_on_error:
                    raise ValueError(
                        f"""
                        Timeout: {timeout} secs; generating {count} unique
                        random integers within the range {min}-{max}
                        """
                    )
                else:
                    return None
            if unique:
                generated_numbers.add(min + secrets.randbelow(max - min + 1))
            else:
                return [min + secrets.randbelow(max - min + 1) for _ in range(count)]

        return list(generated_numbers)


def true_random_choice(
    choices: list | dict,
    count: int = 1,
    unique: bool = False,
    timeout: int = 10,
    api_key: str = _RANDOM_ORG_API_KEY,
    fail_on_error: bool = False,
) -> Generator[Any, None, None]:
    """
    Makes a choice from a given set of choices.
    It uses true random numbers from random.org or falls back to pseudo-random numbers using urandom.
    If count is greater than 1, it yields the choices.

    Args:
        choices (list | dict): The set of choices to choose from. It can be a list or a dictionary.
        count (int, optional): The number of integers to fetch. Default is 1.
        unique (bool, optional): If True, the fetched integers will be unique within this call. Default is False.
        timeout (int, optional): The timeout for the function to complete. Default is 10 seconds.
            It has to main uses:

            As a timeout for the request to random.org (in seconds).

            As a timeout for the function to complete (in seconds). This is used to ensure that the function
            does not run for too long, especially when generating unique random integers.

        api_key (str, optional): The API key to use for the request. If None, the value of the **_RANDOM_ORG_API_KEY**
            environment variable will be used. Default is None.
        fail_on_error (bool, optional): If True, raise an exception if the request to random.org fails.

    Note:
        If a dictionary is passed as choices, the choice will be made from the values of the dictionary.
        It is not possible to make a choice from the keys of the dictionary.
        Also it is assumed that the values of the dictionary are primitive types (int, str, etc.). If the values
        are complex types a TypeError exception will be raised.

    Yields:
        Any: A random element of the given choices set. If unique is True the yielded elements will be unique.

        None: If count is greater than 1 and fail_on_error is False and it is not possible to generate unique
        random integers given the range.

    Raises:
        TypeError: If choices is not a list or a dictionary.
        TypeError: If the values of the dictionary are not primitive types (int, float, str, bool, NoneType).
        ValueError: If count is less than 1.
        ValueError: If choices is empty.

    See Also:
        :func:`get_true_random_integers` function for more information on how the random integers are generated

        :ref: random.org API https://api.random.org/json-rpc/4/basic

        :ref: Python random numbers https://docs.python.org/3/library/secrets.html#random-numbers

    Examples:

        >>> true_random_choice([1, 2, 3, 4, 5])
        4

        >>> true_random_choice([1, 2, 3, 4, 5], count=3)
        2
        5
        1

    """
    # Check arguments sanity
    if isinstance(choices, dict):
        choices = list(choices.values())
        # check if the values of the dictionary are primitive types
        if not all(isinstance(choice, (int, float, str, bool, type(None))) for choice in choices):
            raise TypeError("The values of the dictionary must be primitive types (int, float, str, bool, NoneType)")
    elif isinstance(choices, list):
        pass
    else:
        raise TypeError("choices must be a list or a dictionary")

    # choices can't be empty
    if not choices:
        raise ValueError("choices can't be empty")

    if count < 1:
        raise ValueError("count must be greater than 0")

    # Get the random integers
    random_integers = get_true_random_integers(
        count, 1, len(choices), timeout=timeout, api_key=api_key, unique=unique, fail_on_error=fail_on_error
    )
    if not random_integers:
        yield None
    else:
        # yield the choices
        selected_choices = [choices[i - 1] for i in random_integers]
        yield from selected_choices


def get_true_random_string(
    length,
    valid_characters: list[str] | str = _ALPHANUMERIC_CHARACTERS,
    unique: bool = False,
    timeout: int = 10,
    api_key: str = _RANDOM_ORG_API_KEY,
    fail_on_error: bool = False,
) -> str | None:
    """
    Generates a random string of alphanumeric characters.

    Args:
        length (int): The length of the random string to generate. Must be between 1 and _MAX_STRING_LENGTH.
        valid_characters (list[str] | str, optional): The list of valid characters to use for the random string.
            default is _ALPHANUMERIC_CHARACTERS which is equal to `string.ascii_letters + string.digits`.
        unique (bool, optional): If True, the generated string will be unique within this call. Default is False.
        timeout (int, optional): The timeout for the function to complete. Default is 10 seconds.
        api_key (str, optional): The API key to use for the request. If None, the value of the _RANDOM_ORG_API_KEY.
        fail_on_error (bool, optional): If True, raise an exception if the request to random.org fails.

    Returns:
        str: The generated random string.

        None: If it is not possible to generate unique random integers given the range and the timeout.

    Raises:
        ValueError: If length is less than 1 or greater than _MAX_STRING_LENGTH.
        ValueError: If length is greater than the number of valid characters and unique is True.
        TypeError: If valid_characters is not a list or a string.

    See Also:
        :func:`true_random_choice` function for more information on how the random integers are generated

    Examples:

            >>> generate_random_string(10)
            's2F4f2D4f2'

            >>> generate_random_string(10, unique=True)
            's2F4f2D4f2'

            >>> generate_random_string(10, valid_characters="abc")
            'cbbabccacc'

            >>> generate_random_string(10, valid_characters="abc", unique=True)
            'cbbabccacc'

            >>> generate_random_string(10, valid_characters=["a", "b", "c"])
            'cbbabccacc'

            >>> generate_random_string(10, valid_characters=["a", "b", "c"], unique=True)
            'cbbabccacc'
    """

    # Check arguments sanity
    if not (1 <= length < _MAX_STRING_LENGTH):
        raise ValueError(f"length must be between 1 and {_MAX_STRING_LENGTH}")

    if unique and (length > len(valid_characters)):
        raise ValueError(
            f"length {length} must be less than or equal to the number of valid characters {len(valid_characters)}"
        )

    if isinstance(valid_characters, str):
        valid_characters = list(valid_characters)
    elif isinstance(valid_characters, list):
        pass
    else:
        raise TypeError("valid_characters must be a list or a string")

    # Return the result
    character_generator = true_random_choice(
        valid_characters, count=length, unique=unique, timeout=timeout, api_key=api_key, fail_on_error=fail_on_error
    )
    if not character_generator:
        return None

    result = ""
    for character in character_generator:
        result += character

    return result


def check_random_org_quota(count, timeout=10, api_key=_RANDOM_ORG_API_KEY, fail_on_error=False) -> bool:
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
        RandomQuotaExceeded: If the quota is exceeded and fail_on_error is True.
    """

    remaining_quota = get_random_org_quota(timeout=timeout, api_key=api_key, fail_on_error=fail_on_error)
    if remaining_quota is None:
        if fail_on_error:
            raise requests.exceptions.RequestException("Failed to get quota from random.org")
        else:
            return False

    if remaining_quota >= count:
        return True
    else:
        if fail_on_error:
            raise RandomQuotaExceeded(
                message=f"Quota exceeded trying to generate {count} bytes",
                requested_bits=count * 8,
                remaining_bits=remaining_quota * 8,
            )
        else:
            return False


def get_random_org_quota(timeout=10, api_key=_RANDOM_ORG_API_KEY, fail_on_error=False) -> int | None:
    """
    Get the remaining quota on random.org in bytes.

    Args:
        timeout (int, optional): The timeout for the request to random.org (in seconds). Default is 10 seconds.
        api_key (str, optional): The API key to use for the request. If None, the value of the _RANDOM_ORG_API_KEY.
        fail_on_error (bool, optional): If True, raise an exception if the request to random.org fails.
            Default is False.

    Returns:
        int: The remaining quota in bytes.
        None: If it is not possible to get the quota.

    Raises:
        requests.exceptions.RequestException: If the request to random.org fails and fail_on_error is True.
        requests.exceptions.Timeout: If the request to random.org times out and fail_on_error is True.
    """

    try:
        if api_key:
            # Check quota with an API key
            response = requests.post(_RANDOM_ORG_API_URL, json=_RANDOM_ORG_QUOTA_PAYLOAD, timeout=timeout)
            if response.status_code == 200:
                remaining = response.json()["result"]["bitsLeft"]
                return int(remaining / 8)
            else:
                # If error on request raise Exception or return False
                if fail_on_error:
                    raise requests.exceptions.RequestException(
                        f"Request to random.org failed with status code {response.status_code}"
                    )
                else:
                    return None
        else:
            # Check quota without an API key. It uses the requesting IP address.
            response = requests.get(_RANDOM_ORG_QUOTA_URL, timeout=timeout)

            if response.status_code == 200:
                # Response is in bits, convert to bytes. Assume 8 bits per byte.
                quota = int(int(str(response.text)) / 8)
                return quota
            else:
                # If error on request raise Exception or fallback to pseudo-random numbers
                if fail_on_error:
                    raise requests.exceptions.RequestException(
                        f"Request to random.org failed with status code {response.status_code}"
                    )

    except requests.exceptions.Timeout:
        if fail_on_error:
            raise requests.exceptions.Timeout(f"Request to random.org timed out after {timeout} seconds")
        else:
            return None

    except requests.exceptions.RequestException as e:
        # Handle timeout or other request errors raise Exception or fallback to pseudo-random numbers
        if fail_on_error:
            raise requests.exceptions.RequestException(f"Request to random.org failed with exception {e}")
        else:
            return None

    return None


def main():
    """
    Random Generator

    This script generates random strings or random integers based on the provided arguments.

    Arguments:
    -a, --api-key: The API key to use for the request. If None, the value of the _RANDOM_ORG_API_KEY environment
    -c, --count: Number of random strings to generate (default: 1)
    -C, --choice: Make a choice from a given set of choices. It can be a list or a dictionary. Optional arguments:
    number of choices to make (default: 1), unique (default: False)
    -f, --fail-on-error: Fail on error when making API requests
    -h, --help: Show this help message and exit
    -i, --integers: Generate random integers
    -l, --length: Length of the random string (default: 10)
    -m, --min: Minimum value for random integers (default: 0)
    -q, --quota: Check the quota for n bytes (default: 0)
    -s, --string: Generate a random string
    -t, --timeout: Timeout for the API request (default: 10)
    -u, --unique: Generate unique random integers or strings
    -v, --valid-characters: Valid characters for the random string
    -V, --version: Show the version
    -x, --max: Maximum value for random integers (default: 100)
    """

    parser = argparse.ArgumentParser(description="Random Generator")
    parser.add_argument("-a", "--api-key", type=str, help="The API key to use for the request")
    parser.add_argument("-s", "--string", action="store_true", help="Generate a random string")
    parser.add_argument("-l", "--length", type=int, default=10, help="Length of the random string. Default is 10")
    parser.add_argument(
        "-c", "--count", type=int, default=1, help="Number of random strings to generate. Default is 1"
    )
    parser.add_argument(
        "-v", "--valid-characters", type=str, help="Valid characters for the random string. Default is alphanumeric"
    )
    parser.add_argument("-i", "--integers", action="store_true", help="Generate random integers")
    parser.add_argument("-u", "--unique", action="store_true", help="Generate unique random integers or strings")
    parser.add_argument(
        "-t", "--timeout", type=int, default=10, help="Timeout for the API request. Default is 10 seconds"
    )
    parser.add_argument("-m", "--min", type=int, default=0, help="Minimum value for random integers. Default is 0")
    parser.add_argument("-x", "--max", type=int, default=100, help="Maximum value for random integers. Default is 100")
    parser.add_argument("-f", "--fail-on-error", action="store_true", help="Fail on error when making API requests")
    parser.add_argument("-V", "--version", action="version", version="%(prog)s 1.0.0")
    parser.add_argument("-q", "--quota", type=int, default=0, help="Check the quota. Default is 0")
    parser.add_argument(
        "-C",
        "--choice",
        type=str,
        help="""Make a choice from a given set of choices. It can be a list or a dictionary. Optional arguments: number
            of choices to make (default: 1), unique (default: False)""",
    )

    args = parser.parse_args()

    count = args.count if args.count else 1
    unique = args.unique if args.unique else False
    timeout = args.timeout if args.timeout else 10
    api_key = args.api_key if args.api_key else _RANDOM_ORG_API_KEY
    fail_on_error = args.fail_on_error if args.fail_on_error else False

    if args.string:
        length = args.length if args.length else 10
        valid_characters = args.valid_characters if args.valid_characters else None

        for _ in range(count):
            if valid_characters:
                random_string = get_true_random_string(
                    length,
                    valid_characters,
                    unique=unique,
                    timeout=timeout,
                    api_key=api_key,
                    fail_on_error=fail_on_error,
                )
            else:
                random_string = get_true_random_string(length, unique=unique, timeout=timeout, api_key=api_key)
            print(random_string)
    elif args.integers:
        min_value = args.min if args.min else 0
        max_value = args.max if args.max else 100

        random_integers = get_true_random_integers(
            count, min_value, max_value, timeout, unique=unique, fail_on_error=fail_on_error, api_key=api_key
        )
        print(random_integers)
    elif args.quota:
        remaining_quota = get_random_org_quota(timeout, fail_on_error=fail_on_error, api_key=api_key)
        if args.quota:
            if remaining_quota >= args.quota:
                print(f"Enough quota for {args.quota:,} bytes. Remaining bytes={remaining_quota:,}")
            else:
                print(f"Not enough quota for {args.quota:,} bytes. Remaining bytes={remaining_quota:,}")
        else:
            print(f"Remaining quota={remaining_quota:,} bytes")
    elif args.choice:
        try:
            choices = json.loads(args.choice)
        except (TypeError, json.JSONDecodeError):
            print(
                """ERROR: choices must be a list or a dictionary as a string.
                The dictionary must be in valid JSON format.""",
                file=sys.stderr,
            )
            parser.print_usage()
            exit(1)

        random_choices = true_random_choice(
            choices, count, unique=unique, timeout=timeout, fail_on_error=fail_on_error, api_key=api_key
        )
        print([x for x in random_choices])
    else:
        parser.print_usage()


if __name__ == "__main__":
    main()
