"""
Utility methods to aid usage of Skipjack.

Usage:

Send some data (as a list of tuples as per the DEFAULT_LIST) and
call create_response(data) and get a Transaction model object back.

"""
from django.conf import settings

from skipjack.helpers import PaymentHelper, StatusHelper
from skipjack.models import Transaction, Status
from skipjack.signals import payment_was_successful, payment_was_flagged


DEFAULT_LIST = [
    ('SerialNumber', settings.SKIPJACK_SERIAL_NUMBER),
    ('DeveloperSerialNumber', settings.SKIPJACK_DEVELOPER_SERIAL_NUMBER)
]

SZ_DEFAULT_LIST = [
    ('szSerialNumber', settings.SKIPJACK_SERIAL_NUMBER),
    ('szDeveloperSerialNumber', settings.SKIPJACK_DEVELOPER_SERIAL_NUMBER)
]


def create_response(data):
    """
    Creates a Transaction in the database based on the returned data from
    Skipjack to an authorize request.
    Sends signals payment_was_successful or payment_was_flagged.
    
    """
    helper = PaymentHelper(defaults=DEFAULT_LIST)
    response_dict = helper.get_response(data)
    response_dict['test_request'] = settings.SKIPJACK_DEBUG
    response = Transaction.objects.create_from_dict(response_dict)
    if response.is_approved:
        payment_was_successful.send(sender=response)
    else:
        payment_was_flagged.send(sender=response)
    return response


def get_transaction_status(order_number, transaction_id=None):
    """
    Returns a textual description of either the latest transaction associated
    with the request, or the status of the specified transaction_id.
    
    order_number is required because that's what Skipjack wants. You can't send
    the transaction_id to Skipjack for the transaction status method.
    
    We return two critical parts of the Skipjack response: a numeric code
    indicating the status, and a textual string interpreting the numeric code.
    
    Naturally, the SerialNumber and DeveloperSerialNumber fields are prefixed
    with 'sz' making them totally inconsistent with the authorize request above.
    
    """
    helper = StatusHelper(defaults=SZ_DEFAULT_LIST)
    response_dict = helper.get_response(order_number,
                                        transaction_id=transaction_id)
    response = Status(**response_dict)
    return response
    