import os
from typing import Dict

from national_rail_pipeline.api import RailQuerier


def format_departure_board(departure_board) -> Dict:
    """
    This function formats the raw departure board information into a more user friendly
    python dictionary.  The most important fields are extracted from the API response
    and stored in the dictionary.
    :param departure_board: The Nation Rail API response which contains departure board
    information for a single station
    :return: A python dictionary which contains the most important departure board
    information. The python dictionary is much easier to manipulate than the raw
    API response.
    """
    formatted_departure_board = {}

    formatted_departure_board["locationName"] = departure_board.locationName
    formatted_departure_board["trainServices"] = []

    for trainservice in departure_board.trainServices.service:
        service = {}
        service["origin"] = trainservice.origin.location[0].locationName
        service["destination"] = trainservice.destination.location[0].locationName
        service["sched_dep"] = trainservice.std
        service["curr_dep"] = trainservice.etd
        service["platform"] = trainservice.platform
        service["operator"] = trainservice.operator
        service["length"] = trainservice.length
        service["id"] = trainservice.serviceID

        service["calling_points"] = []
        if (
            trainservice.subsequentCallingPoints
            and trainservice.subsequentCallingPoints.callingPointList
        ):
            for cp in trainservice.subsequentCallingPoints.callingPointList[
                0
            ].callingPoint:
                calling_point = {}
                calling_point["name"] = cp.locationName
                calling_point["isCancelled"] = cp.isCancelled
                calling_point["sched_time"] = cp.st
                calling_point["est_time"] = cp.et
                service["calling_points"].append(calling_point)

        formatted_departure_board["trainServices"].append(service)

    return formatted_departure_board


def print_departure_board(formatted_departure_board: Dict) -> None:
    """
    This function is use to print a formatted departure board to standard out.
    The printed departure board includes the following information for each
    service soon to be departing from that station: Destination, Platform,
    Scheduled Departure, Expected Departure
    :param formatted_departure_board:
    :return: Prints a departure board to standard out
    """
    white_space = "\n\n"
    boarder = 39 * "-" + "\n"
    departure_board_header = format_departure_board_header()
    train_services = formatted_departure_board["trainServices"]
    formatted_train_services = [
        format_train_service_for_departure_board(x) for x in train_services
    ]
    departure_board = white_space + boarder + departure_board_header
    for formatted_train_service in formatted_train_services:
        departure_board += formatted_train_service
    departure_board += boarder + white_space
    print(departure_board)


def format_departure_board_header() -> str:
    """
    Produces a departure board header which includes underlined column names
    with appropriate white space
    :return: The departure board header
    """
    column_headings = "Destination        Plat. SchDep ExpDep \n"
    lower_boarder = 18 * "-" + " " + 5 * "-" + " " + 6 * "-" + " " + 7 * "-" + "\n"
    departure_board_header = column_headings + lower_boarder
    return departure_board_header


def format_train_service_for_departure_board(train_service: Dict) -> str:
    """
    Format information for each train service in such a way that makes it
    visually consistent with the other components of the departure board.
    :param train_service: A dictionary which contains information
    about a single train service
    :return: A formatted string which contains train service information
    """
    destination = format_field(train_service["destination"], 18)
    platform = format_field(train_service["platform"], 5)
    sched_dep = format_field(train_service["sched_dep"], 6)
    curr_dep = format_field(train_service["curr_dep"], 7)
    formatted_train_service = f"{destination} {platform} {sched_dep} {curr_dep}\n"
    return formatted_train_service


def format_field(field: str, max_field_length: int) -> str:
    """
    This function is used to format a field to a specified field length.
    If a field is shorter than the max length then the remaining characters
    will be padded with whitespace.  If the field is longer than the max
    length then the field will be sliced and a full stop (.) will be
    appended to the end of the field to reflect this.  If the field
    is None then a ? with whitespace appended will be returned.
    :param field: The field that needs to be formatted
    :param max_field_length: The max length of the output field
    :return: The formatted output field which is of length equal to max_field_length
    """
    if field is None:
        padding = (max_field_length - 1) * " "
        return "?" + padding
    field_length = len(field)
    if field_length <= max_field_length:
        padding = (max_field_length - field_length) * " "
        return field + padding
    else:
        return field[: max_field_length - 1] + "."


if __name__ == "__main__":
    """A main body to execute the logic to fetch departure board information from
    the National Rail Api and then output a pretty departure board to standard out.
    """
    station = os.getenv("STATION", "LHS")
    rail_querier = RailQuerier()
    departure_board = rail_querier.get_departure_board(station)
    formatted_depature_board = format_departure_board(departure_board)
    print_departure_board(formatted_depature_board)
