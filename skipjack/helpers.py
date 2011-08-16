"""Helpers for performing operations directly with Skipjack."""
import csv
import urllib
import urllib2

from django.conf import settings

from skipjack import SKIPJACK_POST_URL, SKIPJACK_TEST_POST_URL, \
                     SKIPJACK_TEST_STATUS_POST_URL, SKIPJACK_STATUS_POST_URL, \
                     SKIPJACK_TEST_STATUS_CHANGE_POST_URL, \
                     SKIPJACK_STATUS_CHANGE_POST_URL
from skipjack.models import CURRENT_STATUS_CHOICES, PENDING_STATUS_CHOICES


class PaymentHelper(object):
    """Helper for sending payment data and receiving data from Skipjack."""
    def __init__(self, defaults):
        self.defaults = defaults
        if settings.SKIPJACK_DEBUG:
            self.endpoint = SKIPJACK_TEST_POST_URL
        else:
            self.endpoint = SKIPJACK_POST_URL
    
    def get_response(self, data):
        """Gets the response from Skipjack from the supplied data."""
        final_data = self.defaults + data  # These must be lists, not dicts.
        request_string = urllib.urlencode(final_data)
        response = urllib2.urlopen(self.endpoint, data=request_string).read()
        response_dict = dict(zip(*[row for row in csv.reader(
                                                           response.split("\n"),
                                                           delimiter=',',
                                                           quotechar='"')]))
        return response_dict


class StatusHelper(object):
    """
    Helper for sending a transaction status request and
    receiving data from Skipjack about the status of said transaction.
    
    This is based from the Order Number, not the Transaction Id that we get
    from Skipjack when we make an authorize request.
    
    NOTE: Because the transaction id will change when a transaction is settled,
          we allow for the transaction id being not present by returning the
          latest transaction status details in that case as though no
          transaction id was present. It's up to you to check for this changed
          transaction id value.
    
    
    """
    def __init__(self, defaults):
        self.defaults = defaults
        if settings.SKIPJACK_DEBUG:
            self.endpoint = SKIPJACK_TEST_STATUS_POST_URL
        else:
            self.endpoint = SKIPJACK_STATUS_POST_URL
    
    def get_response(self, order_number, transaction_id=None):
        """Gets the response from Skipjack from the supplied data."""
        final_data = self.defaults + [('szOrderNumber', order_number)]
        request_string = urllib.urlencode(final_data)
        response = urllib2.urlopen(self.endpoint, data=request_string).read()
        # First line of the response is the header, lines that follow are
        # individual transactions relating to the given order_number.
        response = [row for row in csv.reader(response.strip().split('\n'),
                                              delimiter=',', quotechar='"')][1:]
        response_dict = None
        if transaction_id:
            for row in response:
                if len(row) is 9 and row[6] == transaction_id:
                    response_dict = {'amount': row[1],
                                     'code': row[2],
                                     'message': row[3],
                                     'order_number': row[4],
                                     'date': row[5],
                                     'transaction_id': row[6],
                                     'approval_code': row[8],
                                     'batch_number': row[8]}
                    break
        if not response_dict:
            # Transaction id either not specified, or no longer present,
            # return the latest Transaction from Skipjack...
            row = response[-1]
            if len(row) is 9:
                response_dict = {'amount': row[1],
                                 'code': row[2],
                                 'message': row[3],
                                 'order_number': row[4],
                                 'date': row[5],
                                 'transaction_id': row[6],
                                 'approval_code': row[8],
                                 'batch_number': row[8]}
        # Add the Status Code interpretation directly for more detail than the
        # status_message return value gives us.
        if response_dict:
            status = []
            if response_dict['code'][0] != '0':
                status.append(
                    dict(CURRENT_STATUS_CHOICES)[int(response_dict['code'][0])])
            if response_dict['code'][1] != '0':
                status.append(
                    dict(PENDING_STATUS_CHOICES)[int(response_dict['code'][1])])
            response_dict['message_detail'] = ', '.join(status)
        return response_dict


class ChangeStatusHelper(object):
    """
    Helper for sending transaction change status request and
    receiving data from Skipjack about the request.
    
    This is based on the Skipjack Transaction Id, and not the Order Number.
    So much for consistency. We could submit request using the Order number
    to Skipjack, but we want to tie this directly to specific transactions.
    Naturally transaction id will change when a transaction is settled. Ouch.
    
    """
    def __init__(self, defaults):
        self.defaults = defaults
        if settings.SKIPJACK_DEBUG:
            self.endpoint = SKIPJACK_TEST_STATUS_CHANGE_POST_URL
        else:
            self.endpoint = SKIPJACK_STATUS_CHANGE_POST_URL
    
    def get_response(self, data):
        """Gets the response from Skipjack from the supplied data."""
        final_data = self.defaults + data  # These must be lists, not dicts.
        request_string = urllib.urlencode(final_data)
        response = urllib2.urlopen(self.endpoint, data=request_string).read()
        # First line of the response is the header, second line is the
        # main response detail OR a textual description of an error.
        response = [row for row in csv.reader(response.strip().split('\n'),
                                              delimiter=',', quotechar='"')][1:]
        response_dict = None
        row = response[-1]
        if len(row) is 7:
            response_dict = {'amount': row[1],
                             'desired_status': row[2],
                             'status': row[3],
                             'message': row[4],
                             'order_number': row[5],
                             'transaction_id': row[6]}
        return response_dict