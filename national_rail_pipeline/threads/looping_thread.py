import threading
import time
import logging

from typing import Optional


class LoopingThread(threading.Thread):
    def __init__(
        self,
        name: str = Optional[None],
        daemon: bool = False,
        interval_timeout: float = 1 / 10,
        required_precision: Optional[float] = None,
    ):
        """A Base class for Looping threads.
        This class will run anything in its loop method at a set interval.

        Args:
            name (str, optional): A friendly name to be used for logging.
            daemon (bool, optional): Whether to run the thread as a daemon.
            interval_timeout (float, optional): Interval this thread will use to run.
            required_precision (float, optional): The required precision for
                the interval. If set to None, defaults to 1/10 of the interval.
        """
        threading.Thread.__init__(self, name=name, daemon=daemon)
        self.logger = logging.getLogger(f"{__name__.split('.')[0]}.{name}")
        # TODO come up with a better solution

        self.stop_event_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.set_stop_event()

        self.interval_timeout = interval_timeout
        self.required_precision = (
            required_precision
            if required_precision is not None
            else self.interval_timeout / 10
        )
        self.last_run_time = 0

    def get_stop_event(self) -> bool:
        with self.stop_event_lock:
            return self.stop_event.is_set()

    def set_stop_event(self) -> None:
        with self.stop_event_lock:
            self.stop_event.set()

    def unset_stop_event(self) -> None:
        with self.stop_event_lock:
            self.stop_event.clear()

    def stop(self) -> None:
        self.set_stop_event()
        self.logger.debug("Thread stopped externally.")

    def setup(self) -> None:
        """This is to be overwritten by subclass.
        It is executed once after the start of the thread."""
        raise NotImplementedError

    def loop(self) -> None:
        """This is to be overwritten by subclass.
        It is looped continuously until the thread is stopped."""
        raise NotImplementedError

    def teardown(self) -> None:
        """This is to be overwritten by subclass.
        It is executed once, when the thread is stopped."""
        raise NotImplementedError

    def run(self) -> None:
        try:
            self.logger.debug(f"Executing setup for thread {self.name}")
            self.setup()
        except Exception as e:
            # TODO add better exception logic
            self.logger.exception(e)
            try:
                self.logger.critical(
                    f"Trying to perform emergency teardown for thread {str(self)}"
                )
                self.teardown()
            except Exception as te:
                self.logger.error("Exception during teardown")
                self.logger.exception(te)
            return

        self.unset_stop_event()

        self.logger.debug("Executing loop for thread " + self.name)
        while not self.stop_event.is_set():

            if (time.time() - self.last_run_time) < self.interval_timeout:
                self.stop_event.wait(self.required_precision)
                continue

            self.last_run_time = time.time()
            try:
                self.loop()
            except Exception as e:
                self.logger.exception(e)
                try:
                    self.logger.critical(
                        f"Trying to perform emergency teardown for thread {str(self)}"
                    )
                    self.teardown()
                except Exception as te:
                    self.logger.error("Exception during teardown")
                    self.logger.exception(te)
                return
        try:
            self.logger.debug(f"Performing normal teardown for thread {str(self)}")
            self.teardown()
        except Exception as e:
            self.logger.error("Exception during teardown")
            self.logger.exception(e)
