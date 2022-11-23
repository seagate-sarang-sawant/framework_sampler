# -*- coding: utf-8 -*-

"""This module has implements decorator to catch FT exceptions."""

from commons.exceptions import FTException


class FTFailOn:
    """
    This class has implemented to use as a decorator.

    Usage : decorate the avocado testMethod with this class decorator
            if the test method generates the specified exception. It will mark test as failure and
            execute the handler funFTion which was provide with argument.
    Note  : 1. If exception has not provided, default FTException will be considered.
    """

    def __init__(
            self,
            routine_func,
            exception_type=FTException,
            routine_params=None):
        """
        Initializer FTFailOn to exception, routine func, params and description.

        exception_type : exception to handled.
        routine_func : function which need to be called as an exception handler(routine)
        routine_param : Arguments for exception handler function(routine)
        routine_params will be tuple containing the object attribute names in string format
        """
        self.exception = exception_type
        self.routine_func = routine_func
        self.routine_params = routine_params
        self.routine_param_values = []

    def __call__(self, func):
        """FT exception caught and calling the failure routine."""
        def __wrap(*args, **kwargs):
            try:
                try:
                    return func(*args, **kwargs)
                except self.exception as details:
                    # Here FT exception caught and calling the failure routine
                    # functions with the parameters
                    if self.routine_params:
                        for i in self.routine_params:
                            # Here args[0] will be the decorated function obj
                            # TestError: if the object attribute is not found
                            try:
                                self.routine_param_values.append(
                                    getattr(args[0], i))
                            except AttributeError as err:
                                raise FTException(err) from err
                    self.routine_func(details, *self.routine_param_values)
            except Exception as exc:
                raise FTException(exc) from exc

        return __wrap
