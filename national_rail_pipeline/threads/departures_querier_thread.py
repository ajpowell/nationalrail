from national_rail_pipeline.threads.looping_thread import LoopingThread
from national_rail_pipeline.api import RailQuerier

from national_rail_pipeline.departure_board_schema import validate_departure_board

from national_rail_pipeline.utils.util import create_directory_if_not_exists

import os
import json
import csv
from threading import Lock

from marshmallow import ValidationError

from typing import List, Dict, Union, Optional


class DeparturesQuerier(LoopingThread):
    def __init__(
        self,
        crs_codes: List[str],
        out_directory: str,
        log_file_access_lock: Lock,
        interval_timeout: float,
        required_precision: Optional[float] = None,
        name: str = "DeparturesQuerier",
    ):
        """Periodically queries the National Rail API for new departures
         at a given list of stations.
         It then writes these departures to files.
         These files are archived at a given interval

        Args:
            crs_codes (List[str]): CRS codes of stations to query
            out_directory (str): Directory to store log results
            log_file_access_lock (threading.Lock): Locks access to the live log files
            archive_access_lock (threading.Lock): Locks access to the archived log files
            archive_interval (float): Interval at which files are moved to archive
            interval_timeout (float): Interval between queries in seconds
            required_precision (float, optional): required precision for the interval
        """
        LoopingThread.__init__(
            self,
            name=name,
            interval_timeout=interval_timeout,
            required_precision=required_precision,
            daemon=True,
        )

        self._live_file_access_lock = log_file_access_lock

        self.crs_codes = crs_codes
        self.out_directory = out_directory

        self._rail_querier = RailQuerier()
        self.out_file_paths = {}

    def setup(self) -> None:
        self.logger.debug("Setting up")

        with self._live_file_access_lock:
            create_directory_if_not_exists(self.out_directory)

        self.out_file_paths = {
            crs: os.path.join(self.out_directory, f"{crs}.csv")
            for crs in self.crs_codes
        }
        self.logger.debug("Set up Complete")

    def loop(self) -> None:
        failed_crs_codes = []
        for crs in self.crs_codes:
            try:
                result = self._rail_querier.get_departure_board(crs)
            except Exception as e:
                self.logger.exception(f"ERROR DURING API QUERY {e}")
                failed_crs_codes.append(crs)
                continue

            try:
                validate_departure_board(result)
            except ValidationError as e:
                self.logger.debug(result)
                self.logger.exception(f"VALIDATION THREW ERROR {e}")
                failed_crs_codes.append(crs)
                continue

            if not result.trainServices:
                self.logger.warning(f"No services currently scheduled from {crs}")
                failed_crs_codes.append(crs)
                continue

            row_results = self.__flatten_departure_board(result)
            self.__append_to_csv_file(self.out_file_paths[crs], row_results)
            self.logger.debug(f"Wrote new logs for {crs}")

        if len(failed_crs_codes) > 0:
            self.logger.warning(f"Failed to get departures for {failed_crs_codes}")
        successful_departures = [
            item for item in self.crs_codes if item not in failed_crs_codes
        ]
        self.logger.info(f"Successfully got new departures for {successful_departures}")
        return successful_departures, failed_crs_codes

    def teardown(self) -> None:
        pass

    def __flatten_departure_board(
        self, result
    ) -> List[Dict[str, Union[str, int, float, bool, None]]]:
        return_row_list = []

        for trainservice in result.trainServices.service:
            service = {}
            service["service_from"] = result.locationName
            service["dt_timestamp"] = str(result.generatedAt)
            service["origin"] = trainservice.origin.location[0].locationName
            service["destination"] = trainservice.destination.location[0].locationName
            service["sched_dep"] = trainservice.std
            service["curr_dep"] = trainservice.etd
            service["platform"] = trainservice.platform
            service["operator"] = trainservice.operator
            service["length"] = trainservice.length
            service["id"] = trainservice.serviceID

            calling_points = []
            if (
                trainservice.subsequentCallingPoints
                and trainservice.subsequentCallingPoints.callingPointList
            ):
                for cp in trainservice.subsequentCallingPoints.callingPointList[
                    0
                ].callingPoint:
                    calling_point = {}
                    calling_point["name"] = cp.locationName
                    calling_point["is_cancelled"] = cp.isCancelled
                    calling_point["sched_time"] = cp.st
                    calling_point["est_time"] = cp.et
                    calling_points.append(calling_point)

            service["calling_points"] = json.dumps(calling_points)

            return_row_list.append(service)

        return return_row_list

    def __append_to_csv_file(
        self, file_path: str, rows: List[Dict[str, Union[str, int, float, bool, None]]]
    ):
        with self._live_file_access_lock:
            is_new_file = False
            if not os.path.exists(file_path):
                is_new_file = True

            with open(file_path, "a", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=rows[0].keys())

                if is_new_file:
                    writer.writeheader()

                writer.writerows(rows)
