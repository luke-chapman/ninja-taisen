import logging

# Due to multithreaded simulations and multiple entry points, log-level is set in multiple places
# Changing this value in local code is a useful way to turn on debug logging in all contexts
DEFAULT_LOGGING = logging.INFO
