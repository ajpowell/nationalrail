from national_rail_pipeline.threads.looping_thread import LoopingThread

from national_rail_pipeline.utils.util import create_directory_if_not_exists

from threading import Lock
from datetime import datetime
import os
from typing import Optional


class FileArchiver(LoopingThread):
    def __init__(
        self,
        out_directory: str,
        log_file_access_lock: Lock,
        archive_access_lock: Lock,
        interval_timeout: float,
        required_precision: Optional[float] = None,
        name: str = "FileArchiver",
    ):
        """Periodically queries the National Rail API for new departures
         at a given list of stations.
         It then writes these departures to files.
         These files are archived at a given interval

        Args:
            out_directory (str): Directory to store log results
            log_file_access_lock (threading.Lock): Locks access to the live log files
            archive_access_lock (threading.Lock): Locks access to the archived log files
            interval_timeout (float): Interval at which files are moved to archive
            required_precision (float, optional): required precision for the interval
        """
        LoopingThread.__init__(
            self,
            name=name,
            interval_timeout=interval_timeout,
            required_precision=required_precision,
            daemon=True,
        )

        self.out_directory = out_directory
        self.archive_directory = os.path.join(self.out_directory, "archive")

        self._log_file_access_lock = log_file_access_lock
        self._archive_access_lock = archive_access_lock

        self.is_first_run = True

    def setup(self) -> None:
        self.logger.debug("Setting up")
        with self._log_file_access_lock:
            create_directory_if_not_exists(self.out_directory)
        with self._archive_access_lock:
            create_directory_if_not_exists(self.archive_directory)
        self.logger.debug("Finished Setting Up")

    def loop(self) -> None:
        if self.is_first_run:
            self.logger.info("First Archive run since program start, skipping...")
            self.is_first_run = False
            return

        self.logger.debug("Starting archival of log files")

        file_counter = 0
        with self._log_file_access_lock, self._archive_access_lock:
            for file_name in os.listdir(self.out_directory):
                if file_name.endswith(".csv"):
                    self.__archive_log_file(os.path.join(self.out_directory, file_name))
                    file_counter += 1
        self.logger.info(f"Archived {file_counter} files")

    def teardown(self) -> None:
        pass

    def __archive_log_file(self, file_path: str) -> None:

        file_name, file_ext = os.path.splitext(os.path.basename(file_path))
        time_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        new_file = f"{file_name}-{time_str}{file_ext}"

        destination_file_path = os.path.join(self.archive_directory, new_file)
        self.logger.debug(
            f"Attempting to archive file {file_path} to {destination_file_path}"
        )
        if os.path.exists(destination_file_path):
            self.logger.warning(
                f"File {destination_file_path} already exists. Skipping..."
            )
            return

        os.rename(file_path, destination_file_path)
