# -*- coding: utf-8 -*-
"""
Framework error codes and descriptions.

Provides an error data object to contain the error code and description.
The error object is in the format: NAME_OF_ERROR(code, description).

Helper functions:
    - get_error(): Searches through this module to find error objects based on the provided code
        or description.
    - validate_errors_codes(): Checks for duplicate error codes and missing error descriptions.
"""

import sys
import logging
from dataclasses import dataclass

LOGGER = logging.getLogger(__name__)


@dataclass
class FTError:
    """Provides an error data object to contain the error code and description."""

    code: int
    desc: str


def get_error(info):
    """
     Retrieve an error from a provided error code or error description.

    :param info: Error code (int) or message (str) needed to search with.
    :return: The corresponding error or None.
    """
    glob = globals().copy()
    for _, val in glob.items():
        if isinstance(val, FTError):
            if (isinstance(info, int) and info == val.code) or (
                    isinstance(info, str) and info.lower() in val.desc.lower()):
                return val
    return None


# Test error codes below this line

# Test Case Errors  [1-999]
TEST_FAILED = FTError(1, "Test Failed")
MISSING_PARAMETER = FTError(2, "Missing Parameter")
INVALID_PARAMETER = FTError(3, "Invalid Parameter")

# Product Configuration DataBase Errors
FILE_MISSING = FTError(30001, "File missing")
YAML_SYNTAX_ERROR = FTError(30002, "YAML file syntax error")
INVALID_CONFIG_FILE = FTError(30003, "Invalid configuration file")

