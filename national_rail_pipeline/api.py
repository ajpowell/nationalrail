# Open Live Departure Boards Web Service (OpenLDBWS) API Demonstrator
# Copyright (C)2018 OpenTrainTimes Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
import os

from zeep import Client
from zeep import xsd
from zeep.plugins import HistoryPlugin


class RailQuerier:
    def __init__(self):
        """The RailQuerier object is a central interface for the National Rail API.
        During instantiation of the RailQuerier object it searches for an environment
        variable named "LDB_TOKEN" and expects this variable to hold a valid National
        Rail API token.  The National Rail API is a SOAP implementation and the
        RailQuerier class intends to abstract the logic required to query the API.
        """
        self.LDB_TOKEN = os.environ.get("LDB_TOKEN")
        self.WSDL = (
            "http://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx?ver=2017-10-01"
        )
        if self.LDB_TOKEN == "":
            raise Exception(
                "Please configure your OpenLDBWS token in getDepartureBoardExample!"
            )
        self.history = HistoryPlugin()
        self.client = Client(wsdl=self.WSDL, plugins=[self.history])

    def get_departure_board(self, station_crs_code: str):
        """
        This method is used to query the National Rail API and fetch departure board
        information.  The raw response of the API request is returned to the client.
        :param station_crs_code: The CRS code of the station for which the departure
        board information is desired.
        :return: Raw departure board information returned by the API call
        """
        header = xsd.Element(
            "{http://thalesgroup.com/RTTI/2013-11-28/Token/types}AccessToken",
            xsd.ComplexType(
                [
                    xsd.Element(
                        "{http://thalesgroup.com/RTTI/2013-11-28/Token/types}TokenValue",  # noqa: B950
                        xsd.String(),
                    ),
                ]
            ),
        )
        header_value = header(TokenValue=self.LDB_TOKEN)
        res = self.client.service.GetDepBoardWithDetails(
            numRows=10, crs=station_crs_code, _soapheaders=[header_value]
        )
        return res

    def get_arrival_board(self, station_crs_code: str):
        """
        This method is used to query the National Rail API and fetch arrival board
        information.  The raw response of the API request is returned to the client.
        :param station_crs_code: The CRS code of the station for which the arrival
        board information is desired.
        :return: Raw arrival board information returned by the API call
        """
        header = xsd.Element(
            "{http://thalesgroup.com/RTTI/2013-11-28/Token/types}AccessToken",
            xsd.ComplexType(
                [
                    xsd.Element(
                        "{http://thalesgroup.com/RTTI/2013-11-28/Token/types}TokenValue",  # noqa: B950
                        xsd.String(),
                    ),
                ]
            ),
        )
        header_value = header(TokenValue=self.LDB_TOKEN)
        res = self.client.service.GetArrBoardWithDetails(
            numRows=10, crs=station_crs_code, _soapheaders=[header_value]
        )
        return res

    def get_arr_dep_board(self, station_crs_code: str):
        """
        This method is used to query the National Rail API and fetch arrival and departure board
        information.  The raw response of the API request is returned to the client.
        :param station_crs_code: The CRS code of the station for which the arrival and departure
        board information is desired.
        :return: Raw arrival and departure board information returned by the API call
        """
        header = xsd.Element(
            "{http://thalesgroup.com/RTTI/2013-11-28/Token/types}AccessToken",
            xsd.ComplexType(
                [
                    xsd.Element(
                        "{http://thalesgroup.com/RTTI/2013-11-28/Token/types}TokenValue",  # noqa: B950
                        xsd.String(),
                    ),
                ]
            ),
        )
        header_value = header(TokenValue=self.LDB_TOKEN)
        res = self.client.service.GetArrDepBoardWithDetails(
            numRows=10, crs=station_crs_code, _soapheaders=[header_value]
        )
        return res
