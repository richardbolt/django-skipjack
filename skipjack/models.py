"""Skipjack response models."""
import datetime
from decimal import Decimal
import time

from django.db import models
from django.db.models.signals import pre_delete
from django.utils.encoding import smart_unicode


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


# Map Skipjack return fields to Transaction model fields.
TRANSACTION_MAPPING = {
    'szReturnCode': 'return_code',
    'szOrderNumber': 'order_number',
    'szIsApproved': 'approved',
    'AUTHCODE': 'auth_code',
    'szTransactionAmount': 'amount',
    'szAuthorizationDeclinedMessage': 'auth_decline_message',
    'szCVV2ResponseMessage': 'cvv2_response_message',
    'szCVV2ResponseCode': 'cvv2_response_code',
    'szAVSResponseCode': 'avs_code',
    'szAVSResponseMessage': 'avs_message',
    'szTransactionFileName': 'transaction_id',
    'szCAVVResponseCode': 'cavv_response',
    'szAuthorizationResponseCode': 'auth_response_code',
    # Fields that map directly to what we store in the Transaction.
    'is_live': 'is_live',
    # Fields that don't map to what we store in the Transaction.
    'szSerialNumber': ''
}

# For STATUS change usage.
AUTHORIZED = 1
DENIED = 2
SETTLED = 3
CREDITED = 4
DELETED = 5
ARCHIVED = 6
PRE_AUTHORIZED = 7
SPLIT_SETTLED = 8

PENDING_CREDIT = 1
PENDING_SETTLEMENT = 2
PENDING_DELETED = 3
PENDING_AUTHORIZATION = 4
PENDING_MANUAL_SETTLEMENT = 5
PENDING_RECURRING = 6
SUBMITTED_FOR_SETTLEMENT = 7

CURRENT_STATUS_CHOICES = (
    (0, '---'),
    (1, 'Authorized'),
    (2, 'Denied'),
    (3, 'Settled'),
    (4, 'Credited'),
    (5, 'Deleted'),
    (6, 'Archived'),
    (7, 'Pre-Authorized'),
    (8, 'Split Settled')
)

PENDING_STATUS_CHOICES = (
    (0, '---'),
    (1, 'Pending Credit'),
    (2, 'Pending Settlement'),
    (3, 'Pending Delete'),
    (4, 'Pending Authorization'),
    (5, 'Pending Manual Settlement'),
    (6, 'Pending Recurring'),
    (7, 'Submitted for Settlement')
)

SUCCESSFUL = 'SUCCESSFUL'
UNSUCCESSFUL = 'UNSUCCESSFUL'
NOT_ALLOWED = 'NOT ALLOWED'


class TransactionError(StandardError):
    """Use for Transaction related errors."""
    pass


class TransactionManager(models.Manager):
    """
    To provide:
    
    1. A create_from_dict() shortcut method.
    
    """
    def create_from_dict(self, params):
        """
        Handle creation of a Transaction object directly from a
        dictionary returned by SkipJack.
        """
        kwargs = dict(map(lambda x: (TRANSACTION_MAPPING[x[0]], x[1]),
                          params.items()))
        del kwargs['']  # We mapped szSerialNumber to the empty string.
        # Special cases.
        kwargs['amount'] = int(return_code)
        # Amount is returned as '12002' instead of '120.02'.
        kwargs['amount'] = Decimal(kwargs['amount']) / 100
        return self.create(**kwargs)


class Transaction(models.Model):
    """
    Skipjack Transaction.
    
    Contains the fields returned by a SkipJack Authorize request, plus a few
    that are useful based on getting the transaction status, and providing
    for methods to change the Transaction status.
    
    The transaction_id can be blank, and will be blank if return_code is
    something other than 1. These indicate failed transactions.
    
    WARNING: The transaction_id changes when a transaction moves through
             processing at Skipjack. This does not appear to be documented
             anywhere. For instance, a transaction is authorized, and then
             settle() is called to settle the transaction, then later the
             transaction id will change when the transaction is actually
             settled. This is incredibly annoying.
    
    """
    transaction_id = models.CharField(max_length=18, db_index=True)
    auth_code = models.CharField(max_length=6,  # NB: min_length=6
                                 blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    auth_decline_message = models.CharField(max_length=60, blank=True)
    avs_code = models.CharField('AVS code', max_length=10,
                                choices=AVS_RESPONSE_CODE_CHOICES)
    avs_message = models.CharField('AVS message', max_length=60, blank=True)
    order_number = models.CharField(max_length=20, db_index=True)
    auth_response_code = models.CharField(max_length=6,  # NB: min_length=6
                                          blank=True)
    approved = models.CharField(max_length=1, blank=True,
                                choices=IS_APPROVED_CHOICES,
                                help_text="Check AVS filtering!")
    cvv2_response_code = models.CharField('CVV2 response code',
                                          max_length=2, blank=True,
                                          choices=CVV2_RESPONSE_CODE_CHOICES)
    cvv2_response_message = models.CharField('CVV2 response message',
                                             max_length=60, blank=True)
    return_code = models.IntegerField(choices=RETURN_CODE_CHOICES)
    cavv_response = models.CharField('CAVV response', max_length=2, blank=True,
                                     choices=CAVV_RESPONSE_CODE_CHOICES)
    is_live = models.BooleanField(default=True)
    
    creation_date = models.DateTimeField(auto_now_add=True)
    mod_date = models.DateTimeField(auto_now=True)
    
    # Updated with a self.update_status() call.
    status_text = models.CharField(max_length=50, blank=True)
    current_status = models.PositiveSmallIntegerField(default=0,
                                choices=CURRENT_STATUS_CHOICES)
    pending_status = models.PositiveSmallIntegerField(default=0,
                                choices=PENDING_STATUS_CHOICES)
    status_date = models.DateTimeField(blank=True, null=True)
    
    objects = TransactionManager()
    
    @property
    def is_approved(self):
        """If the transaction was successful, or not."""
        if (self.return_code == 1 and self.auth_code and \
                                      self.auth_response_code):
            return True
        return False
    
    def __unicode__(self):
        return u"Transaction ID: %s, Amount: %s, Auth code: %s" % \
                (self.transaction_id, self.amount, self.auth_response_code)
    
    def get_status(self):
        """
        Updates the current status directly with a call to Skipjack.
        
        You will need to call self.save() to ensure the status_text
        and date are written to the database, should you require it.
        
        NOTE: Skipjack will change the Transaction Id when a transaction moves
              through processing from Authorized to Settled. This is problematic
              and something to watch out for.
        
        """
        from skipjack.utils import get_transaction_status
        status = get_transaction_status(self.order_number,
                                        transaction_id=self.transaction_id)
        self.status_text = status.message_detail
        self.current_status = status.current_status
        self.pending_status = status.pending_status
        self.status_date = status.date
        if status.transaction_id != self.transaction_id:
            self.transaction_id = status.transaction_id
        return status
    
    def update_status(self):
        """Shortcut that updates the status and saves the result."""
        status = self.get_status()
        self.save()
        return status
    update_status.alters_data = True
    
    def _change_status(self, status=None, amount=None):
        """
        Change the Status of the Transaction.
        
        Used when we want to Settle, Refund. etc.
        
        We run some checks based on the current status to see what we will
        allow to happen. For example, we can't allow a Delete on a Settled
        transaction - that would require a Refund/Credit. Skipjack will,
        unfortunately, let you do things you shouldn't like the above example,
        so we'll only allow a subset of what you could do.
        
        """
        from skipjack.utils import change_transaction_status
        return change_transaction_status(self.transaction_id, status, amount)
    
    def settle(self):
        """
        Settle a previously Authorized transaction.
        
        This places an Authorized transaction into the Settlement queue to be
        settled according to the preferences set for the Merchant Account in
        the Skipjack system.
        
        """
        if self.current_status != AUTHORIZED or self.pending_status == \
                                                    SUBMITTED_FOR_SETTLEMENT:
            raise TransactionError(
                'Settlement not allowed for %s transactions' % self.status_text)
        # Need to report back if this request was not successful.
        response = self._change_status('SETTLE')
        if response.status != SUCCESSFUL:
            raise TransactionError('Sorry, Skipjack said %s - %s' % (
                                    response.status, response.message))
    
    def refund(self):
        """Full refund."""
        if self.current_status != SETTLED or self.pending_status:
            raise TransactionError('Transaction must be Settled to refund.')
        response = self._change_status('CREDIT', self.amount)
        if response.status != SUCCESSFUL:
            raise TransactionError('Sorry, Skipjack said %s - %s' % (
                                    response.status, response.message))
    
    def partial_refund(self, amount=None):
        """Partially refund the Transaction."""
        if not amount:
            raise TransactionError('Partial refund requires an amount.')
        if type(amount) is not Decimal:
            amount = Decimal(amount)
        if amount > self.amount:
            raise TransactionError('Partial refund requires the amount '\
                                   'be less than the Transaction amount.')
        if self.current_status != SETTLED or self.pending_status:
            raise TransactionError('Transaction status prevents a partial '\
                                   'refund at this time.')
        response = self._change_status('CREDIT',
                                       amount=amount.quantize(Decimal('0.01')))
        if response.status != SUCCESSFUL:
            raise TransactionError('Sorry, Skipjack said %s - %s' % (
                                    response.status, response.message))
    
    def delete_transaction(self):
        """
        Mark the transaction as deleted. Not for Settled transactions.
        
        You will also want to delete this object if you call this directly.
        
        NOTE: Calling self.delete() will call this automatically so that the
              transaction is deleted (if it can be) from the Skipjack system.
        
        """
        if self.current_status in (SETTLED, CREDITED, ARCHIVED, SPLIT_SETTLED):
            raise TransactionError('Deletion not allowed for %s transactions' %
                                    self.status_text)
        response = self._change_status('DELETE')
        if response.status != SUCCESSFUL:
            raise TransactionError('Sorry, Skipjack said %s - %s' % (
                                    response.status, response.message))
    
    class Meta:
        ordering = ['-creation_date']


def delete_transaction(sender, instance, using, *args, **kwargs):
    """Also delete from Skipjack when a Transaction is deleted from the db."""
    instance.get_status()
    try:
        instance.delete_transaction()
    except TransactionError:
        pass # If the transaction can't be deleted, just ignore the issue.

pre_delete.connect(delete_transaction, sender=Transaction)


class Status(object):
    """
    A helper object for the Transaction Status function.
    
    """
    def __init__(self, **kwargs):
        """
        Initialize from the keyword arguments.
        
        """
        self.transaction_id = None
        self.amount = None
        self.code = None
        self.message = None
        self.message_detail = None
        self.order_number = None
        self.date = None
        self.approval_code = None
        self.batch_number = None
        
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        # Special properties (we don't want to leave these as text):
        if type(self.date) is not datetime.datetime:
            self.date = datetime.datetime.fromtimestamp(
                time.mktime(time.strptime(self.date, "%m/%d/%y %H:%M:%S")))
        if type(self.amount) is not Decimal:
            self.amount = Decimal(self.amount)
        self.current_status = int(self.code[0])
        self.pending_status = int(self.code[1])
    
    def __repr__(self):
        return smart_unicode('<Status: %s>' % str(self))
        
    def __str__(self):
        if self.transaction_id and self.message_detail:
            return smart_unicode('%s - %s' % (self.transaction_id,
                                              self.message_detail))
        elif self.transaction_id:
            return smart_unicode('%s' % self.transaction_id)
        else:
            return smart_unicode('Status unknown')
    
    @property
    def transaction(self):
        """So we can have the transaction object available."""
        if not hasattr(self, '_transaction'):
            try:
                self._transaction = Transaction.objects.get(
                                        transaction_id=self.transaction_id)
            except Transaction.DoesNotExist:
                self._transaction = None
        return self._transaction


class StatusChange(object):
    """
    A helper object for the Change Transaction Status function.
    
    """
    def __init__(self, **kwargs):
        """
        Initialize from the keyword arguments.
        
        """
        self.amount = None
        self.desired_status = None
        self.status = None  # SUCCESSFUL, UNSUCCESSFUL, or NOT_ALLOWED.
        self.message = None
        self.order_number = None
        self.transaction_id = None
        
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        # Special properties (we don't want to leave these as text):
        if type(self.amount) is not Decimal:
            self.amount = Decimal(self.amount)
    
    def __repr__(self):
        return smart_unicode('<ChangeStatus: %s>' % str(self))
        
    def __str__(self):
        if self.transaction_id and self.message:
            return smart_unicode('%s %s - %s' % (self.desired_status,
                                                 self.transaction_id,
                                                 self.status))
        elif self.transaction_id:
            return smart_unicode('%s' % self.transaction_id)
        else:
            return smart_unicode('ChangeStatus unknown')
    
    @property
    def transaction(self):
        """So we can have the transaction object available."""
        if not hasattr(self, '_transaction'):
            try:
                self._transaction = Transaction.objects.get(
                                        transaction_id=self.transaction_id)
            except Transaction.DoesNotExist:
                self._transaction = None
        return self._transaction
        