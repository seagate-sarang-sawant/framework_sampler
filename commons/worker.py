# -*- coding: utf-8 -*-

"""Worker pool to perform similar tasks"""
import logging
import queue
import threading
from typing import Any
from threading import Thread
from commons.constants import NWORKERS

logger = logging.getLogger(__name__)


class WorkQ(queue.Queue):
    def __init__(self, func: Any, maxsize: int) -> None:
        self.lock_req = maxsize != 0
        self.func = func
        self.semaphore = threading.Semaphore(maxsize)
        queue.Queue.__init__(self, maxsize)

    def put(self, item):
        if self.lock_req:
            self.semaphore.acquire()
        queue.Queue.put(self, item)

    def task_done(self):
        if self.lock_req:
            self.semaphore.release()
        queue.Queue.task_done(self)


class Workers(object):
    """ A fixed size thread pool for I/O bound tasks """

    def __init__(self):
        self.w_workers = []
        self.w_workq = None

    def start_workers(self,
                      nworkers: int = NWORKERS,
                      func: Any = None) -> None:
        self.w_workq = WorkQ(func, nworkers)
        for i in range(nworkers):
            w = Thread(target=self.worker)
            w.start()
            self.w_workers.append(w)

    def worker(self):
        while True:
            wq = self.w_workq.get()
            if wq is None:
                self.w_workq.task_done()
                break
            wi = wq.get()
            wq.func(wi)
            wq.task_done()
            self.w_workq.task_done()

    def wenque(self, item):
        self.w_workq.put(item)

    def end_workers(self):
        for i in range(len(self.w_workers)):
            self.w_workq.put(None)
        self.w_workq.join()
        logger.info('shutdown all workers')
        logger.info('Joining all threads to main thread')
        for i in range(len(self.w_workers)):
            self.w_workers[i].join()

