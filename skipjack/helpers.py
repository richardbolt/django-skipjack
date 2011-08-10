import csv
import urllib
import urllib2

from django.conf import settings

from skipjack import SKIPJACK_POST_URL, SKIPJACK_TEST_POST_URL


class PaymentHelper(object):
    """Helper for sending and receiving data from Skipjack."""
    def __init__(self, defaults):
        self.defaults = defaults
        if settings.SKIPJACK_DEBUG:
            self.endpoint = SKIPJACK_TEST_POST_URL
        else:
            self.endpoint = SKIPJACK_POST_URL
    
    def get_response(self, data):
        """Gets the response from Skipjack from the supplied data."""
        final_data = self.defaults + data # These must be lists, not dicts.
        request_string = urllib.urlencode(final_data)
        response = urllib2.urlopen(self.endpoint, data=request_string).read()
        response_dict = dict(zip(*[row for row in csv.reader(response.split("\n"),
                                                             delimiter=',',
                                                             quotechar='"')]))
        return response_dict
