"""
Code for executing natural capital models
"""
import sys
import traceback
from functools import wraps


def print_warning_message(message):
    """
    Write message to sys.stdout
    """
    sys.stdout.write(f"warning: {message}\n")


def print_error_message(message):
    """
    Write message to sys.stderr
    """
    # Flush stdout to keep messages in the correct order. Otherwise we get
    # info messages after the error message.
    sys.stdout.flush()
    sys.stderr.write(f"{message}\n")


def checked_call(function, *args, **kwargs):
    """
    Call a function, passing it the arguments passed in here

    This function handles any exceptions that are thrown during the
    execution of the function. A status code is returned: 0 in case of
    success, 1 in case an exception was thrown.

    When an exception is thrown, error messages are printed, using
    :py:func:`print_error_message`
    """
    status = 1

    try:
        status = function(*args, **kwargs)
    except RuntimeError:
        lines = traceback.format_exc().splitlines()
        for line in lines:
            print_error_message(line)

    return 0 if status is None else status


def checked_call2(function):
    """
    Decorator for executing a function while catching exceptions
    """

    @wraps(function)
    def wrapper(*args, **kwargs):
        status = 1

        # Handle exceptions that are likely user errors. All other
        # exceptions are likely developer/modeller errors and passed on.
        # A user does not care about the stack trace.

        try:
            status = function(*args, **kwargs)
        except RuntimeError:
            lines = traceback.format_exc().splitlines()
            for line in lines:
                print_error_message(line)
        except ValueError as exception:
            print_error_message(exception)

        return 0 if status is None else status

    return wrapper
