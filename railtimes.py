# from national_rail_pipeline.threads.departures_querier_thread import DeparturesQuerier
# from national_rail_pipeline.threads.file_archiver_thread import FileArchiver
# from national_rail_pipeline.utils.config import Config
# from national_rail_pipeline.utils.util import configure_logging
from national_rail_pipeline.api import RailQuerier

from dotenv import load_dotenv
# import sys
import os
import logging
import json
import datetime

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

#     Ver    Author          Date       Comments
#     ===    =============== ========== =======================================
ver = 0.1  # ajpowell        2022-06-14 Initial code


def configure_logging():
    # Initialise logging module
    logging.root.handlers = []
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO
        # level=logging.DEBUG
        )


def main():
    logging.debug('Using API Token: {}'.format(os.environ.get("LDB_TOKEN")))
    logging.info('')

    crs = 'NCL'
    output_file_dirs = datetime.datetime.now().strftime('raw/%Y/%m/%d')
    output_file_name = datetime.datetime.now().strftime('%H%M%S')

    output_file_path = os.path.join(output_file_dirs, output_file_name + '-' + crs + '.json')

    rq = RailQuerier()

    # result = rq.get_departure_board("RDG")
    # result = rq.get_arrival_board("RDG")
    result = rq.get_arr_dep_board(crs)

    # print(response)

    return_row_list = []

    for trainservice in result.trainServices.service:
        logging.debug(trainservice)
        service = {}
        service["service_from"] = result.locationName
        service["dt_timestamp"] = str(result.generatedAt)
        service["origin"] = trainservice.origin.location[0].locationName
        service["origin_crs"] = trainservice.origin.location[0].crs
        service["destination"] = trainservice.destination.location[0].locationName
        service["destination_crs"] = trainservice.destination.location[0].crs
        service["sched_dep"] = trainservice.std
        service["curr_dep"] = trainservice.etd
        service["sched_arr"] = trainservice.sta
        service["curr_arr"] = trainservice.eta
        service["platform"] = trainservice.platform
        service["operator"] = trainservice.operator
        service["operatorCode"] = trainservice.operatorCode
        service["length"] = trainservice.length
        service["id"] = trainservice.serviceID
        service["rsid"] = trainservice.rsid
        service["cancelReason"] = trainservice.cancelReason
        service["delayReason"] = trainservice.delayReason

        # logging.info('{} - {} - Plat. {} - {} -> {}; Sched_dep: {}; Curr_dep: {}'.format(service["id"], service["operator"], service["platform"],service["origin"], service["destination"],  service["sched_dep"], service["curr_dep"]))
        if service["sched_arr"] is None:
            logging.info('{} ({}) - {} - Plat. {} - {} ({}) -> {} ({}); Sched_dep: {}; Curr_dep: {}'.format(service["id"], service["rsid"], service["operatorCode"], service["platform"], service["origin"], service["origin_crs"], service["destination"], service["destination_crs"],  service["sched_dep"], service["curr_dep"]))
        else:
            logging.info('{} ({}) - {} - Plat. {} - {} ({}) -> {} ({}); Sched_arr: {}; Curr_arr: {}'.format(service["id"], service["rsid"], service["operatorCode"], service["platform"], service["origin"], service["origin_crs"], service["destination"], service["destination_crs"],  service["sched_arr"], service["curr_arr"]))

        calling_points = []
        if (trainservice.subsequentCallingPoints and
                trainservice.subsequentCallingPoints.callingPointList):
            for cp in trainservice.subsequentCallingPoints.callingPointList[0].callingPoint:
                calling_point = {}
                calling_point["name"] = cp.locationName
                calling_point["crs"] = cp.crs
                calling_point["is_cancelled"] = cp.isCancelled
                calling_point["sched_time"] = cp.st
                calling_point["est_time"] = cp.et
                calling_points.append(calling_point)

        # service["calling_points"] = json.dumps(calling_points)
        service["calling_points"] = calling_points

        return_row_list.append(service)

    logging.info('')

    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    container_name = 'nationalrail'

    # Connect to existing container
    container_client = blob_service_client.get_container_client(container_name)

    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=output_file_path)

    blob_client.upload_blob(json.dumps(return_row_list))

    logging.info(f'Stored data in : {output_file_path}')
    # print(json.dumps(return_row_list))


if __name__ == "__main__":
    configure_logging()

    # Load the environment variables from .env
    load_dotenv()

    print('')
    logging.info('{} v{}'.format(os.path.basename(__file__), ver))
    logging.info('')

    # Jump to main code
    main()
