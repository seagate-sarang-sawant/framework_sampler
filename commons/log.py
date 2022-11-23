import logging
import os
import sys

from commons import params
"""Custom log level which is more verbose than DEBUG"""
TRACE: int = 5

LOG = logging.getLogger('auto')

__all__ = ['TRACE', 'setup_logging']


def setup_logging(log_level: int = logging.DEBUG):
    """
    Initializes the logging for the whole application.

    Registers special framework logger, configures the logging format and
    sets the verbosity level to `log_level`.

    Register custom verbosity level called TRACE. Here is the example
    how tracing can be done:
            LOG.log(TRACE, 'This is a trace message')

    Note: This function must be invoked before any logging happens.
    """
    logging.addLevelName(TRACE, 'TRACE')
    logger = LOG
    logger.setLevel(log_level)

    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] {%(threadName)s} %(message)s')
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)


def set_log_handlers(log, name, mode='w', level=logging.DEBUG):
    """Set stream and file handlers."""
    fh = logging.FileHandler(name, mode=mode)
    fh.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    log.addHandler(fh)
    log.addHandler(ch)


def initialize_loghandler(log, level=logging.DEBUG) -> None:
    """Initialize test runner logging with stream and file handlers."""
    log.setLevel(level)
    cwd = os.getcwd()
    dir_path = os.path.join(os.path.join(cwd, params.LOG_DIR_NAME, params.LATEST_LOG_FOLDER))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    name = os.path.splitext(os.path.basename(__file__))[0]
    name = os.path.join(dir_path, name + '.log')
    cortxlogging.set_log_handlers(log, name, mode='w')

