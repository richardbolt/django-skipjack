" Skipjack response models. "
from django.db import models

RETURN_CODE_CHOICES = (
    (1, 'Success'),
    (0, 'Comm failure'),
    (-1, 'Error in request'),
    (-35, 'Invalid credit card number'),
    (-37, 'Merchant processor unavailable'),
    (-39, 'Invalid Serial Number'),
    (-51, 'Zip code incorrect'),
    (-52, 'Ship to zip code incorrect'),
    (-53, 'Expiration month incorrect'),
    (-54, 'Expiration month or year incorrect'),
    (-55, 'Street address incorrect'),
    (-56, 'Ship to street address incorrect'),
    (-57, 'Transaction amount incorrect'),
    (-58, 'Merchant name incorrect'),
    (-59, 'Merchant address incorrect'),
    (-60, 'Merchant state incorrect'),
    (-61, 'Ship to state incorrect'),
    (-62, 'Order string incorrect'),
    (-64, 'No phone number'),
    (-65, 'No name'),
    (-66, 'No email'),
    (-67, 'No street address'),
    (-68, 'No city'),
    (-69, 'No state'),
    (-70, 'No zip code'),
    (-71, 'No order number'),
    (-72, 'No account number'),
    (-73, 'No month'),
    (-74, 'No year'),
    (-75, 'No serial number'),
    (-76, 'No transaction amount'),
    (-77, 'No order string'),
    (-78, 'No ship to phone'),
    (-79, 'Name incorrect'),
    (-80, 'Ship to name incorrect'),
    (-81, 'City incorrect'),
    (-82, 'State incorrect'),
    (-83, 'Ship to phone incorrect'),
    (-84, 'Duplicate order number'),
    (-91, 'CVV2 invalid or empty'),
    (-92, 'Approval code incorrect'),
    (-97, 'Fraud rejection'),
    (-98, 'Discount amount incorrect'),
    (-101, 'Invalid Authentication date'),
    (-102, 'Authentication data not allowed'),
    (-118, 'Invalid POST URL'),
    (-119, 'General Error'),
    (-120, 'Invalid record count'),
    (-123, 'Developer Serial Number Invalid')
)

IS_APPROVED_CHOICES = (
    ('', 'Not approved'),
    ('0', 'Declined'),
    ('1', 'Approved')
)

AVS_RESPONSE_CODE_CHOICES = (
    ('A', 'Address (Street) matches, ZIP does not'),
    ('B', 'Address information not provided for AVS check'),
    ('E', 'AVS error'),
    ('G', 'Non-U.S. Card Issuing Bank'),
    ('N', 'No Match on Address (Street) or ZIP'),
    ('P', 'AVS not applicable for this transaction'),
    ('R', 'Retry - System unavailable or timed out'),
    ('S', 'Service not supported by issuer'),
    ('U', 'Address information is unavailable'),
    ('W', 'Nine digit ZIP matches, Address (Street) does not'),
    ('X', 'Address (Street) and nine digit ZIP match'),
    ('Y', 'Address (Street) and five digit ZIP match'),
    ('Z', 'Five digit ZIP matches, Address (Street) does not'),
)

TYPE_CHOICES = (
    ('auth_capture', 'Authorize and Capture'),
    ('auth_only', 'Authorize only'),
    ('credit', 'Credit'),
    ('prior_auth_capture', 'Prior capture'),
    ('void', 'Void'),
)

CVV2_RESPONSE_CODE_CHOICES = (
    ('M', 'Match'),
    ('N', 'No Match'),
    ('P', 'Not Processed'),
    ('S', 'Should have been present'),
    ('U', 'Issuer unable to process request'),
)

CAVV_RESPONSE_CODE_CHOICES = (
    ('', 'CAVV not validated'),
    ('0', 'CAVV not validated because erroneous data was submitted'),
    ('1', 'CAVV failed validation'),
    ('2', 'CAVV passed validation'),
    ('3', 'CAVV validation could not be performed; issuer attempt incomplete'),
    ('4', 'CAVV validation could not be performed; issuer system error'),
    ('5', 'Reserved for future use'),
    ('6', 'Reserved for future use'),
    ('7', 'CAVV attempt - failed validation - '
          'issuer available (U.S.-issued card/non-U.S acquirer)'),
    ('8', 'CAVV attempt - passed validation - '
          'issuer available (U.S.-issued card/non-U.S. acquirer)'),
    ('9', 'CAVV attempt - failed validation - '
          'issuer unavailable (U.S.-issued card/non-U.S. acquirer)'),
    ('A', 'CAVV attempt - passed validation - '
          'issuer unavailable (U.S.-issued card/non-U.S. acquirer)'),
    ('B', 'CAVV passed validation, information only, no liability shift'),
)


RESPONSE_MAPPING = {  # Map Skipjack return fields to Response model fields.
    'szReturnCode': 'return_code',
    'szOrderNumber': 'order_number',
    'szIsApproved': 'approved',
    'AUTHCODE': 'auth_code',
    'szTransactionAmount': 'amount',
    'szAuthorizationDeclinedMessage': 'auth_decline_message',
    'szCVV2ResponseMessage': 'cvv2_response_message',
    'szAVSResponseCode': 'avs_code',
    'szCVV2ResponseCode': 'cvv2_response_code',
    'szAVSResponseMessage': '',
    'szTransactionFileName': 'transaction_id',
    'szCAVVResponseCode': 'cavv_response',
    'szAuthorizationResponseCode': 'auth_response_code',
    # Fields that map directly to what we store in the Response.
    'test_request': 'test_request',
    # Fields that don't map to what we store in the Response.
    'szSerialNumber': ''
}


class ResponseManager(models.Manager):
    " Solely to provide a create_from_dict() shortcut method. "
    def create_from_dict(self, params):
        """
        Handle creation of a Response object directly from a
        dictionary returned by SkipJack.
        """
        kwargs = dict(map(lambda x: (RESPONSE_MAPPING[x[0]], x[1]),
                          params.items()))
        del kwargs['']  # We mapped szSerialNumber to the empty string.
        return self.create(**kwargs)


class Response(models.Model):
    " Response from Skipjack. Contains the fields returned by SkipJack. "
    transaction_id = models.CharField(max_length=18,  # NB: min_length=10
                                      primary_key=True)
    auth_code = models.CharField(max_length=6,  # NB: min_length=6
                                 blank=True)
    amount = models.CharField(max_length=12,  # NB: min_length=3
                              help_text="NB: a value of 500 is 5 dollars.")
    auth_decline_message = models.CharField(max_length=60, blank=True)
    avs_code = models.CharField(max_length=10,
                                choices=AVS_RESPONSE_CODE_CHOICES)
    avs_message = models.CharField(max_length=60, blank=True)
    order_number = models.CharField(max_length=20)
    auth_response_code = models.CharField(max_length=6,  # NB: min_length=6
                                          blank=True)
    approved = models.CharField(max_length=1, blank=True,
                                choices=IS_APPROVED_CHOICES,
                                help_text="Check AVS filtering!")
    cvv2_response_code = models.CharField(max_length=2, blank=True,
                                          choices=CVV2_RESPONSE_CODE_CHOICES)
    cvv2_response_message = models.CharField(max_length=60, blank=True)
    return_code = models.IntegerField(choices=RETURN_CODE_CHOICES)
    cavv_response = models.CharField(max_length=2, blank=True,
                                     choices=CAVV_RESPONSE_CODE_CHOICES)
    test_request = models.BooleanField(default=False)
    
    created = models.DateTimeField(auto_now_add=True)
    
    objects = ResponseManager()
    
    @property
    def is_approved(self):
        " If the transaction was successful, or not. "
        if (self.return_code in (1, '1') and self.auth_code and \
                                      self.auth_response_code):
            return True
        return False
    
    def __unicode__(self):
        return u"Transaction ID: %s, Amount: %s, Auth code: %s" % \
                (self.transaction_id, self.amount, self.auth_response_code)
    
    class Meta:
        ordering = ['-created']

