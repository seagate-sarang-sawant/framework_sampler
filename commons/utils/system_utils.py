# -*- coding: utf-8 -*-

"""Module to maintain system utils."""

import logging
import os
import sys
import shutil
import errno
import threading
import secrets
from collections import deque
from subprocess import Popen, PIPE
from hashlib import md5
from pathlib import Path
from botocore.response import StreamingBody
from commons import constants

if sys.platform == 'win32':
    try:
        import msvcrt
    except ImportError:
        MSVCRT = None
if sys.platform in ['linux', 'linux2']:
    try:
        import fcntl
    except ImportError:
        FCNTL = None

LOGGER = logging.getLogger(__name__)


def umount_dir(mnt_dir: str = None) -> tuple:
    """Function to unmount directory
    :param mnt_dir: Path of mounted directory
    :return: Bool, response"""
    if os.path.ismount(mnt_dir):
        LOGGER.info("Unmounting mounted directory")
        cmd = constants.CMD_UMOUNT.format(mnt_dir)
        resp = run_local_cmd(cmd=cmd)
        if not resp[0]:
            return resp

        while True:
            if not os.path.ismount(mnt_dir):
                break

        remove_dirs(dpath=mnt_dir)

    return True, "Directory is unmounted"


def run_local_cmd(cmd: str = None, env: dict = None,
                  flg: bool = False, chk_stderr: bool = False) -> tuple:
    """
    Execute any given command on local machine(Windows, Linux)
    :param cmd: command to be executed
    :param flg: To get str(proc.communicate())
    :param chk_stderr: Check if stderr is none.
    :return: bool, response.
    """
    if not cmd:
        raise ValueError("Missing required parameter: {}".format(cmd))
    LOGGER.debug("Command: %s", cmd)
    proc = None
    try:
        proc = Popen(cmd, shell=True, env=env, stdout=PIPE, stderr=PIPE)  # nosec (B603)
        output, error = proc.communicate()
        LOGGER.debug("output = %s", str(output))
        LOGGER.debug("error = %s", str(error))
        if flg:
            return True, str((output, error))
        if chk_stderr and error:
            return False, str(error)
        if proc.returncode != 0:
            return False, str(error)
        if b"command not found" in error or \
                b"not recognized as an internal or external command" in error or error:
            return False, str(error)

        return True, str(output)
    except RuntimeError as ex:
        LOGGER.exception(ex)
        return False, ex
    finally:
        if proc:
            proc.terminate()


def calc_checksum(object_ref: object, hash_algo: str = 'md5'):
    """
    Calculate checksum of file or stream
    :param object_ref: Object/File Path or byte/buffer stream
    :param hash_algo: md5 or sha1
    :return:
    """
    read_sz = 8192
    csum = None
    file_hash = md5()  # nosec
    if hash_algo != 'md5':
        raise NotImplementedError('Only md5 supported')
    if isinstance(object_ref, StreamingBody):
        chunk = object_ref.read(amt=read_sz)
        while chunk:
            file_hash.update(chunk)
            chunk = object_ref.read(amt=read_sz)
        return file_hash.hexdigest()
    if os.path.exists(object_ref):
        size = Path(object_ref).stat().st_size

        with open(object_ref, 'rb') as file_ptr:
            if size < read_sz:
                buf = file_ptr.read(size)
            else:
                buf = file_ptr.read(read_sz)
            while buf:
                file_hash.update(buf)
                buf = file_ptr.read(read_sz)
            csum = file_hash.hexdigest()

    return csum


def cleanup_dir(dpath: str) -> bool:
    """
    Remove all files, links, directory recursively inside dpath
    :param dpath: Absolute directory path.
    :return: True/False
    """
    for filename in os.listdir(dpath):
        file_path = os.path.join(dpath, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except OSError as error:
            LOGGER.exception("*ERROR* An exception occurred in %s: %s", cleanup_dir.__name__,
                             error)
            return False

    return True


def list_dir(dpath: str) -> list:
    """
    List directory from dpath
    :param dpath: Directory path.
    """
    try:
        flist = os.listdir(dpath)
        LOGGER.debug("List: %s", str(flist))
    except IOError as error:
        LOGGER.exception("*ERROR* An exception occurred in %s: %s", list_dir.__name__, error)
        return []

    return flist


def mkdirs(pth):
    """
    Make Directory
    :param pth: Directory path
    """
    try:
        os.makedirs(pth, exist_ok=True)
    except OSError as erroros:
        if erroros.errno != errno.EEXIST:
            raise
    return os.path.exists(pth)


def remove_dirs(dpath: str) -> bool:
    """
    Remove directory and hierarchy
    :param dpath: Directory path.
    :return:boolean based on cleanup.
    """
    try:
        shutil.rmtree(dpath)
    except IOError as error:
        LOGGER.exception("*ERROR* An exception occurred in %s: %s", remove_dirs.__name__, error)
        return False

    return True


def create_file(fpath: str, count: int, dev: str = "/dev/zero", b_size: str = "1M") -> tuple:
    """
    Create file using dd command
    :param fpath: File path
    :param count: size of the file in MB
    :param dev: Input file used
    :param b_size: block size
    :return:
    """
    proc = None
    try:
        cmd = constants.CREATE_FILE.format(dev, fpath, b_size, count)
        LOGGER.debug(cmd)
        proc = Popen(cmd, shell=True, stderr=PIPE, stdout=PIPE, encoding="utf-8")  # nosec (B603)
        output, error = proc.communicate()
        LOGGER.debug("output = %s", str(output))
        LOGGER.debug("error = %s", str(error))
        if proc.returncode != 0:
            if os.path.isfile(fpath):
                os.remove(fpath)
            raise IOError(f"Unable to create file. command: {cmd}, error: {error}")

        return os.path.exists(fpath), ", ".join([output, error])
    except RuntimeError as ex:
        LOGGER.exception(ex)
        return fpath, ex
    finally:
        if proc:
            proc.terminate()


def remove_file(file_path: str = None):
    """
    This function is used to remove file at specified path
    :param file_path: Path of file to be deleted
    :return: (Boolean, Response)
    """
    try:
        os.remove(file_path)

        return True, "Success"
    except BaseException as error:
        LOGGER.exception("*ERROR* An exception occurred in %s: %s", remove_file.__name__, error)
        return False, error


class FileLock:

    def __init__(self, lock_file):
        self.lock_file = lock_file
        self.fmutex = None

    def file_lock(self, lock_file, non_blocking=False):
        """
        Uses the :func:`msvcrt.locking` function to hard lock the lock file on
        Windows systems.
        """

        if sys.platform == 'win32':
            open_mode = os.O_RDWR | os.O_CREAT | os.O_TRUNC
            try:
                self.fmutex = os.open(self.lock_file, open_mode)
            except OSError:
                pass
            else:
                try:
                    msvcrt.locking(self.fmutex, msvcrt.LK_LOCK, 1)
                except (IOError, OSError):
                    os.close(self.fmutex)
                    return None, False
                else:
                    LOGGER.debug("Lock file created.")
            return self.fmutex, True
        else:
            if not lock_file.startswith('/'):
                # If Not an absolute path name, prefix in $HOME/.runner
                fname = os.path.join(os.getenv('HOME'), '.runner', lock_file)

            fdir = os.path.dirname(fname)
            if not os.path.exists(fdir):
                os.makedirs(fdir)

            try:
                self.fmutex = open(fname, "rb+")
            except (OSError, IOError):
                self.fmutex = open(fname, "wb+")
            try:
                flags = fcntl.LOCK_EX
                if non_blocking:
                    flags |= fcntl.LOCK_NB
                fcntl.flock(self.fmutex.fileno(), flags)
            except IOError:
                return None, False

        return self.fmutex, True

    def file_unlock(self, fmutex, path=''):
        """
        Unlock the file lock
        :param path: Lock file path
        :param fmutex: File lock
        :return:
        """
        if sys.platform == 'win32':
            msvcrt.locking(fmutex, msvcrt.LK_UNLCK, 1)
            os.close(fmutex)
            self.remove_lck_file(path)
        else:
            fcntl.flock(fmutex.fileno(), fcntl.LOCK_UN)
            fmutex.close()
            self.remove_lck_file(path)

    def remove_lck_file(self, path):
        """Remove lock file."""
        try:
            os.remove(path)
        # Probably another instance of the application
        # that acquired the file lock.
        except FileNotFoundError:
            pass
        except OSError:
            pass


class LRUCache:
    """
    In memory cache for storing test id and test node information
    """

    def __init__(self, size: int) -> None:
        self.maxsize = size
        self.fifo = deque()
        self.table = dict()
        self._lock = threading.Lock()

    def store(self, key: str, value: str) -> None:
        """
        Stores the key and value and evicts left most old entry.
        :param key:
        :param value:
        """
        self._lock.acquire()
        if key not in self.table:
            self.fifo.append(key)
        self.table[key] = value

        if len(self.fifo) > self.maxsize:
            del_key = self.fifo.popleft()
            try:
                del self.table[del_key]
            except KeyError as ke:
                pass
        self._lock.release()

    def lookup(self, key: str) -> str:
        """
        Lookup cache for key.
        :param key:
        :return: val of entry
        """
        self._lock.acquire()
        try:
            val = self.table[key]
        finally:
            self._lock.release()
        return val

    def delete(self, key: str) -> None:
        """
        Removes the table entry. The fifo list entry is removed whenever we
        cache is full.
        """
        self._lock.acquire()
        try:
            del self.table[key]
        except KeyError as ke:
            pass
        try:
            self.fifo.remove(key)
        except ValueError as ve:
            pass
        finally:
            self._lock.release()

    def get_keys(self):
        return self.table.keys()        # expensive

class InMemoryDB(LRUCache):
    """In memory storage"""

    def pop_one(self) -> tuple:
        """
        Pop one table entry randomly.
        """
        self._lock.acquire()
        keys = list(self.table.keys())
        if len(keys) == 0:
            self._lock.release()
            return False, False
        key = secrets.choice(keys)
        try:
            val = self.table.pop(key)
        finally:
            self._lock.release()
        return key, val
