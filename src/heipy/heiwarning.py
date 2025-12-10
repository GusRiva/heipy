import warnings
from .colors import *


class HeiWarning(UserWarning):
    pass


class HeiDeprecationWarning(DeprecationWarning):
    """
    Custom deprecation warning for heipy that is visible by default.

    Unlike Python's standard DeprecationWarning (which is hidden by default),
    this warning is always shown to help users migrate to new APIs.
    """
    pass


def custom_warning_format(message, category, filename, lineno, line=None):
    if category == HeiDeprecationWarning or (hasattr(category, '__name__') and 'Deprecation' in category.__name__):
        return f"{RED}[DeprecationWarning]{RESET} {message} (in {filename}, line {lineno})\n"
    return f"{RED}[HeiWarning]{RESET} {message} (in {filename}, line {lineno})\n"

warnings.formatwarning = custom_warning_format

# Make HeiDeprecationWarning visible by default (unlike standard DeprecationWarning)
warnings.simplefilter('always', HeiDeprecationWarning)