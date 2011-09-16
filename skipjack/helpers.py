"""Helpers for performing operations directly with Skipjack."""
import csv
import datetime
from decimal import Decimal
import re
import urllib
import urllib2

from django.conf import settings

from skipjack import SKIPJACK_POST_URL, SKIPJACK_TEST_POST_URL, \
                     SKIPJACK_TEST_STATUS_POST_URL, SKIPJACK_STATUS_POST_URL, \
                     SKIPJACK_TEST_STATUS_CHANGE_POST_URL, \
                     SKIPJACK_STATUS_CHANGE_POST_URL, \
                     SKIPJACK_TEST_CLOSE_OPEN_BATCH_POST_URL, \
                     SKIPJACK_CLOSE_OPEN_BATCH_POST_URL, \
                     SKIPJACK_TEST_REPORT_DOWNLOAD_URL, \
                     SKIPJACK_REPORT_DOWNLOAD_URL
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
        """
        Gets the response from Skipjack from the supplied data.
        
        Data must be coerced to a list so we can ensure the Skipjack serial
        numbers go first, and in the correct order ('SerialNumber' followed by
        'DeveloperSerialNumber') when we call urllib.urlencode in PaymentHelper.
        
        """
        if type(data) is dict:
            data = d.items()
        elif type(data) is tuple:
            data = list(data)
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
                                 'approval_code': row[7],
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


class StatusHistoryHelper(object):
    """
    Helper for sending a transaction status request and
    receiving data from Skipjack about the status of said transaction.
    
    This is based from the Order Number, not the Transaction Id that we get
    from Skipjack when we make an authorize request.
    
    This helper differs from the StatusHelper in that it returns the entire
    history of the given order_number along with Transaction Ids, amounts,
    and so forth.
    
    
    """
    def __init__(self, defaults):
        self.defaults = defaults
        if settings.SKIPJACK_DEBUG:
            self.endpoint = SKIPJACK_TEST_STATUS_POST_URL
        else:
            self.endpoint = SKIPJACK_STATUS_POST_URL
    
    def get_response(self, order_number):
        """Gets the response from Skipjack from the supplied data."""
        final_data = self.defaults + [('szOrderNumber', order_number)]
        request_string = urllib.urlencode(final_data)
        response = urllib2.urlopen(self.endpoint, data=request_string).read()
        # First line of the response is the header, lines that follow are
        # individual transactions relating to the given order_number.
        response = [row for row in csv.reader(response.strip().split('\n'),
                                              delimiter=',', quotechar='"')][1:]
        responses = []
        for row in response:
            if len(row) is 9:
                response_dict = {'amount': row[1],
                                 'code': row[2],
                                 'message': row[3],
                                 'order_number': row[4],
                                 'date': row[5],
                                 'transaction_id': row[6],
                                 'approval_code': row[7],
                                 'batch_number': row[8]}
                # Add the Status Code interpretation directly for more detail than the
                # status_message return value gives us.
                status = []
                if response_dict['code'][0] != '0':
                    status.append(
                        dict(CURRENT_STATUS_CHOICES)[int(response_dict['code'][0])])
                if response_dict['code'][1] != '0':
                    status.append(
                        dict(PENDING_STATUS_CHOICES)[int(response_dict['code'][1])])
                response_dict['message_detail'] = ', '.join(status)
                responses.append(response_dict)
        return responses


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


class CloseBatchHelper(object):
    """
    Helper for sending a close current batch request and receiving data from
    Skipjack.
    
    """
    def __init__(self, defaults):
        self.defaults = defaults
        if settings.SKIPJACK_DEBUG:
            self.endpoint = SKIPJACK_TEST_CLOSE_OPEN_BATCH_POST_URL
        else:
            self.endpoint = SKIPJACK_CLOSE_OPEN_BATCH_POST_URL
    
    def get_response(self):
        """Gets the response from Skipjack (no supplied data required)."""
        request_string = urllib.urlencode(self.defaults)
        response = urllib2.urlopen(self.endpoint, data=request_string).read()
        response = [row for row in csv.reader(response.strip().split('\n'),
                                              delimiter=',', quotechar='"')]
        response_dict = None
        row = response[0]
        if len(row) is 12:
            response_dict = {'status': row[1]}
        return response_dict


class ReportHelper(object):
    """
    Helper for getting Report API data from Skipjack.
    
    """
    def __init__(self, defaults):
        self.defaults = defaults
        if settings.SKIPJACK_DEBUG:
            self.endpoint = SKIPJACK_TEST_REPORT_DOWNLOAD_URL
        else:
            self.endpoint = SKIPJACK_REPORT_DOWNLOAD_URL
    
    def get_response(self, data):
        """Gets the response from Skipjack from the supplied data."""
        final_data = self.defaults + data  # These must be lists, not dicts.
        request_string = urllib.urlencode(final_data)
        response = urllib2.urlopen(
            SKIPJACK_TEST_REPORT_DOWNLOAD_URL, data=request_string).read()
        response_data = re.search(
                r'<!--\sBegin\sData\s-->(?P<data>.*)<!--\sEnd\sData\s-->',
                response, re.M|re.S).group('data').replace('<br>\r\n',
                                                           '\n').strip()
        response_csv = list(csv.reader(response_data.split("\n"),
                                       delimiter=',', quotechar='"'))
        response_list = []
        headers = response_csv[0]
        date_re = re.compile(r"""
            (?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<year>\d{4})\s
            (?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2})\s
            (?P<am_pm>AM|PM)""", re.VERBOSE)
        for row in response_csv[1:]:
            as_dict = dict(zip(*[item for item in (headers, row)]))
            for key, val in as_dict.items():
                if not key:
                    del as_dict[key]
                if key[-6:] == 'Amount':
                    # Convert currencies to a decimal value.
                    # Report API returns $123.45 and ($123.45) for these fields.
                    if val[0] == '(':
                        as_dict[key] = Decimal('-%s' % val[2:-1])
                    else:
                        as_dict[key] = Decimal(val[1:])
                if key[-4:] == 'Date':
                    # Convert to a Python datetime.datetime object.
                    # NB: Could just be lazy and use the dateutil.parser module,
                    # but I'd rather avoid introducing the dependency.
                    match = date_re.match(val)
                    hour = int(match.group('hour'))
                    if match.group('am_pm') == 'PM' and hour != 12:
                        hour += 12
                    as_dict[key] = datetime.datetime(
                                    year=int(match.group('year')),
                                    month=int(match.group('month')),
                                    day=int(match.group('day')),
                                    hour=hour,
                                    minute=int(match.group('minute')),
                                    second=int(match.group('second')))
            response_list.append(as_dict)
        return response_list