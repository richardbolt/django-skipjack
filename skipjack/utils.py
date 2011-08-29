"""
Utility methods to aid usage of Skipjack.

Included utility functions:
    create_transaction(data)

    get_transaction_status(order_number, transaction_id=None)

    change_transaction_status(transaction_id, desired_status, amount=None)

"""
from decimal import Decimal

from django.conf import settings

from skipjack.helpers import PaymentHelper, StatusHelper, ChangeStatusHelper, \
                             CloseBatchHelper, StatusHistoryHelper
from skipjack.models import Transaction, Status, StatusChange, \
                            CLOSE_BATCH_STATUS_CHOICES, \
                            SETTLED, CREDITED, SPLIT_SETTLED
from skipjack.signals import payment_was_successful, payment_was_flagged


DEFAULT_LIST = [
    ('SerialNumber', settings.SKIPJACK_SERIAL_NUMBER),
    ('DeveloperSerialNumber', settings.SKIPJACK_DEVELOPER_SERIAL_NUMBER)
]

SZ_DEFAULT_LIST = [
    ('szSerialNumber', settings.SKIPJACK_SERIAL_NUMBER),
    ('szDeveloperSerialNumber', settings.SKIPJACK_DEVELOPER_SERIAL_NUMBER)
]


def create_transaction(data):
    """
    Creates a Transaction in the database based on the returned data from
    Skipjack to an authorize request.
    Sends signals payment_was_successful or payment_was_flagged.
    
    """
    helper = PaymentHelper(defaults=DEFAULT_LIST)
    response_dict = helper.get_response(data)
    response_dict['is_live'] = not settings.SKIPJACK_DEBUG
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


def get_order_transaction_history(order_number):
    """
    Returns a list of Status objects representing the transaction history
    of the given order.
    
    """
    helper = StatusHistoryHelper(defaults=SZ_DEFAULT_LIST)
    response_list = helper.get_response(order_number)
    history = []
    for response_dict in response_list:
        history.append(Status(**response_dict))
    return history


def change_transaction_status(transaction_id, desired_status, amount=None,
                              force_settlement=True):
    """
    Changes a specified transaction to the desired status if Skipjack can.
    
    Returns a textual description of the response from Skipjack.
    
    """
    helper = ChangeStatusHelper(defaults=SZ_DEFAULT_LIST)
    data = [('szTransactionId', transaction_id),
            ('szDesiredStatus', desired_status)]
    if amount:
        data.append(('szAmount', str(amount)))
    if desired_status.lower() in ('settle', 'credit'):
        if force_settlement:
            data.append(('szForceSettlement', '1'))
        else:
            data.append(('szForceSettlement', '0'))
    response_dict = helper.get_response(data)
    response = StatusChange(**response_dict)
    return response


def close_current_batch():
    """
    Close the current (open) batch.
    
    Returns a textual description of the response from Skipjack.
    
    """
    helper = CloseBatchHelper(defaults=SZ_DEFAULT_LIST)
    response_dict = helper.get_response()
    response = dict(CLOSE_BATCH_STATUS_CHOICES)[response_dict['status']]
    return response


def amount_paid(order_number):
    """
    Iterates through the status history for the given order and calculates
    the amount paid by adding the amounts for Settled, Credited, or
    Split Settled transactions.
    
    """    
    amount = Decimal('0.00')
    for trans in get_order_transaction_history(order_number):
        if trans.current_status in (SETTLED, CREDITED, SPLIT_SETTLED):
            amount += trans.amount
    return amount
    