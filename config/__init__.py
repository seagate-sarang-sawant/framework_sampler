# -*- coding: utf-8 -*-

"""Configs are initialized here."""
import os
import sys
import re
import munch
from typing import List
from commons.params import COMMON_CONFIG
from commons.utils import config_utils


def split_args(sys_cmd: List):
    """split args and make it compliant."""
    eq_splitted = list()
    for item in sys_cmd:
        if item.find('=') != -1:
            eq_splitted.extend(item.split('='))
        else:
            eq_splitted.extend([item])
    return eq_splitted


pytest_args = sys.argv
proc_name = os.path.split(pytest_args[0])[-1]
target_filter = re.compile(".*--target")
pytest_args = split_args(pytest_args)  # sanitize
target = None
if proc_name == 'pytest' and '--target' in pytest_args:
    # This condition will execute when args ore in format ['--target=<target name'>]
    target = list(filter(target_filter.match, pytest_args))[0].split("=")[1].lower()

if target and proc_name in ["pytest"]:
    _use_ssl = ('-s' if '-s' in pytest_args else (
        '--use_ssl' if '--use_ssl' in pytest_args else None))
    use_ssl = pytest_args[
        pytest_args.index(_use_ssl) + 1] if _use_ssl else True
    os.environ["USE_SSL"] = str(use_ssl)

    _validate_certs = ('-c' if '-c' in pytest_args else (
        '--validate_certs' if '--validate_certs' in pytest_args else None))
    validate_certs = pytest_args[
        pytest_args.index(_validate_certs) + 1] if _validate_certs else True
    os.environ["VALIDATE_CERTS"] = str(validate_certs)

CMN_CFG = config_utils.read_yaml(fpath=COMMON_CONFIG)[1]
cmn_cfg = munch.munchify(CMN_CFG)
