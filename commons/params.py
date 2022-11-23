# -*- coding: utf-8 -*-

"""Config files path."""
import os
import tempfile

LOG_FILE = 'framework-sampler.log'

SCRIPT_HOME = os.getcwd()  # Fetches you CWD of the pytest or runner process.
CONFIG_DIR = 'config'
LOG_DIR_NAME = 'log'
LATEST_LOG_FOLDER = 'latest'
LOG_DIR = os.path.join(SCRIPT_HOME, LOG_DIR_NAME)

COMMON_CONFIG = os.path.join(CONFIG_DIR, 'common_config.yaml')
