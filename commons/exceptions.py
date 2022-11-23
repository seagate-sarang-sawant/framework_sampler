# -*- coding: utf-8 -*-

"""Framework and product responses specific exception."""

import logging

from pprint import pformat
from commons import errorcodes as errcodes

LOGGER = logging.getLogger(__name__)


class FTException(Exception):
    """Intended for use to raise test errors with using error codes."""

    def __init__(self, msg=None) -> None:
        """
        Create a test exception
        :param msg: String error message from user.
        """
        super().__init__()
        self.message = msg

    def __str__(self):
        """Representation of this exception."""
        return f"TestException: with Error Message {self.message}:"


class EncodingNotSupported(Exception):
    """Intended for use to raise encoding errors."""

    def __init__(self, msg=None) -> None:
        """
        Create a encoding exception
        :param msg: String error message from user.
        """
        super().__init__()
        self.message = msg

    def __str__(self):
        """Representation of this exception."""
        return f"EncodingException: with Error Message {self.message}:"
