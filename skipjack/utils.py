"""
Utility methods to aid usage of Skipjack.

Usage:

Send some data (as a list of tuples as per the DEFAULT_LIST) and
call create_response(data) and get a Response model object back.

"""
from django.conf import settings

from skipjack.helpers import PaymentHelper
from skipjack.models import Response
from skipjack.signals import payment_was_successful, payment_was_flagged


DEFAULT_LIST = [
    ('SerialNumber', settings.SKIPJACK_SERIAL_NUMBER),
    ('DeveloperSerialNumber', settings.SKIPJACK_DEVELOPER_SERIAL_NUMBER)
]


def create_response(data):
    """
    Creates a Response in the database based on the returned data from
    Skipjack.
    Sends signals payment_was_successful or payment_was_flagged.
    """
    helper = PaymentHelper(defaults=DEFAULT_LIST)
    response_dict = helper.get_response(data)
    response_dict['test_request'] = settings.SKIPJACK_DEBUG
    response = Response.objects.create_from_dict(response_dict)
    if response.is_approved:
        payment_was_successful.send(sender=response)
    else:
        payment_was_flagged.send(sender=response)
    return response


