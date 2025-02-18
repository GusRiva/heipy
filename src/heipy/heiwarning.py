import warnings
from .colors import *


class HeiWarning(UserWarning):
    pass

def custom_warning_format(message, category, filename, lineno, line=None):
    return f"{RED}[HeiWarning]{RESET} {message} (in {filename}, line {lineno})\n"

warnings.formatwarning = custom_warning_format