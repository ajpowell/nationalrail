import threading
import time
import logging


from national_rail_pipeline.threads.departures_querier_thread import DeparturesQuerier
from national_rail_pipeline.threads.file_archiver_thread import FileArchiver
from national_rail_pipeline.utils.config import Config
from national_rail_pipeline.utils.util import configure_logging


def run() -> None:
    config = Config(
        application_name="National Rail Pipeline",
        description="An application concerned with National Rail API Ingestion",
    )
    logger = logging.getLogger("national_rail_pipeline")
    configure_logging(logger, debug=config.run_config["DEBUG"])
    config.log_config()

    # Set up various locks for file accesss
    live_log_file_access_lock = threading.Lock()
    archive_access_lock = threading.Lock()

    threads = []

    departures_querier_thread = DeparturesQuerier(
        crs_codes=config.run_config["STATIONS_TO_QUERY"],
        out_directory=config.run_config["LOG_FILE_DIRECTORY"],
        log_file_access_lock=live_log_file_access_lock,
        interval_timeout=config.run_config["QUERY_FREQUENCY_SECONDS"],
        required_precision=config.run_config["QUERY_FREQUENCY_PRECISION_SECONDS"],
    )

    file_archiver_thread = FileArchiver(
        out_directory=config.run_config["LOG_FILE_DIRECTORY"],
        log_file_access_lock=live_log_file_access_lock,
        archive_access_lock=archive_access_lock,
        interval_timeout=config.run_config["LOG_FILE_ROLLOVER_PERIOD_SECONDS"],
        required_precision=config.run_config[
            "LOG_FILE_ROLLOVER_PERIOD_PRECISION_SECONDS"
        ],
    )

    threads.extend([departures_querier_thread, file_archiver_thread])

    logger.debug("Starting threads")
    for thread in threads:
        thread.start()

    # Main Loop
    logger.debug("Starting main loop")
    while True:
        try:
            time.sleep(1)
            # logger.info("Sleeping!")
        except KeyboardInterrupt:
            time.sleep(1)
            logger.error("Received KILL-Signal")
            break

    for thread in threads:
        thread.stop()

    for thread in threads:
        thread.join(6)
        logger.debug("Thread " + str(thread) + " stopped.")


if __name__ == "__main__":
    run()
