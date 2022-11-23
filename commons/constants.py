# -*- coding: utf-8 -*-

"""All common constant params from test automation project.
While python module/class specific params can be added to to them itself if
they are coupled with the module/class.
"""
#from typing import Final  # needs python 3.8

#: NWORKERS specifies number of worker (python) threads  in a worker pool.
NWORKERS = 32

LOCAL_S3_CERT_PATH = "/etc/ssl/clients/ca.crt"
PIP_CONFIG = "/etc/pip.conf"

CREATE_FILE = "dd if={} of={} bs={} count={} iflag=fullblock"
CMD_UMOUNT = "umount {}"