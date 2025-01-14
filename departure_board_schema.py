"""This module contains the schema definition of the Departure Board response which is
returned by the National Rail API.  The schema is used to validate that the response
conforms to the schema and all expected fields exist and are of the expected type.
marshmallow is used to create the schema objects and perform the validation.  The schema
is heavily nested hence the requirement for a number of schema layers.
"""
from marshmallow import Schema, fields, INCLUDE
from zeep.helpers import serialize_object


def validate_departure_board(departure_board):
    """
    This function is used to validate the departure board.  The departure board is
    fist serialised and then the contents of the serialised object is validated
    using the marshmallow schema.  If the validation fails then a
    marshmallow.ValidationError will be raised, this should be handled by the
    client.  If the validation succeeds then the response will be returned.
    :param departure_board: This is the departure board object returned by the API
    :return: return the response if an exception is not raised
    """
    serialised_departure_board = serialize_object(departure_board)
    result = DepartureBoardSchema().load(serialised_departure_board)
    return result


class CallingPointSchema(Schema):
    class Meta:
        unknown = INCLUDE

    locationName = fields.Str(required=True)  # noqa: N815
    isCancelled = fields.Bool(required=True, allow_none=True)  # noqa: N815
    st = fields.Str(required=True, allow_none=True)
    et = fields.Str(required=True, allow_none=True)


class CallingPointListSchema(Schema):
    class Meta:
        unknown = INCLUDE

    callingPoint = fields.List(  # noqa: N815
        fields.Nested(CallingPointSchema, required=True), required=True
    )


class SubsequentCallingPointsSchema(Schema):
    class Meta:
        unknown = INCLUDE

    callingPointList = fields.List(  # noqa: N815
        fields.Nested(CallingPointListSchema, required=True), required=True
    )


class TrainServiceSchema(Schema):
    class Meta:
        unknown = INCLUDE

    std = fields.Str(required=True, allow_none=True)
    etd = fields.Str(required=True, allow_none=True)
    platform = fields.Str(required=True, allow_none=True)
    operator = fields.Str(required=True)
    length = fields.Field(required=False, allow_none=True)
    serviceID = fields.Str(required=True)  # noqa: N815
    origin = fields.Dict(required=True)
    destination = fields.Dict(required=True)
    subsequentCallingPoints = fields.Nested(  # noqa: N815
        SubsequentCallingPointsSchema, required=True, allow_none=True
    )


class TrainServicesSchema(Schema):
    class Meta:
        unknown = INCLUDE

    service = fields.List(fields.Nested(TrainServiceSchema), required=True)


class DepartureBoardSchema(Schema):
    class Meta:
        unknown = INCLUDE

    locationName = fields.Str(required=True)  # noqa: N815
    crs = fields.Str(required=True)
    trainServices = fields.Nested(  # noqa: N815
        TrainServicesSchema, required=True, default={"service": []}, allow_none=True
    )
