# -*- coding: utf-8 -*-

"""
Python library which have config related operations using package
like config parser, yaml etc.
"""
import json
import logging
import os
import shutil
import yaml
import commons.errorcodes as cterr

LOG = logging.getLogger(__name__)


def read_yaml(fpath: str) -> tuple:
    """
    Read yaml file and return dictionary/list of the content.

    :param str fpath: Path of yaml file to be read
    :return: Boolean, Data
    """
    if os.path.isfile(fpath):
        with open(fpath) as fin:
            try:
                data = yaml.safe_load(fin)
            except yaml.YAMLError as exc:
                err_msg = "Failed to parse: {}\n{}".format(fpath, str(exc))
                LOG.error(err_msg)
                try:
                    data = yaml.load(fin.read(), Loader=yaml.Loader)
                except yaml.YAMLError as exc:
                    err_msg = "Failed to parse: {}\n{}".format(fpath, str(exc))
                    LOG.error(err_msg)
                    return False, exc

    else:
        err_msg = "Specified file doesn't exist: {}".format(fpath)
        LOG.error(err_msg)
        return False, cterr.FILE_MISSING

    return True, data

def create_content_json(path: str, data: object, ensure_ascii=True) -> str:
    """
    Function to create json file.

    :param ensure_ascii:
    :param path: json file path is to be created.
    :param data: Data to write in json file
    :return: path of the file.
    """
    with open(path, 'w') as outfile:
        json.dump(data, outfile, ensure_ascii=ensure_ascii)

    return path


def read_content_json(fpath: str, mode='r') -> dict:
    """
    Function to read json file.

    :param mode:
    :param fpath: Path of the json file
    :return: Data of the json file
    """
    with open(fpath, mode) as json_file:
        data = json.loads(json_file.read())

    return data
