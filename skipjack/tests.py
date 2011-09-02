"""
Testing for the basic operation of django-skipjack.

"""
import copy
import random

from django.utils import unittest
from django.conf import settings

from skipjack.models import Transaction
from skipjack.utils import create_transaction


class RandomOrderNumber(object):
    """
    For generating random numbers for the OrderNumber variable without
    having to specify an order number for each new Transaction.
    
    """
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return ''.join(random.sample('123456789', 3))


def del_list_item(list_dict, key):
    """
    Removes a given "key" from a list of two member tuples/lists of the form
    where dict(list_dict) would succeed.
    
    Returns the modified list.
    
    """
    index = 0
    for item in list_dict:
        if item[0] == key:
            list_dict.pop(index)
            break
        index += 1
    return list_dict
    
#------------
# Tests Below
class SkipjackTestCase(unittest.TestCase):
    """
    Run tests on the Skipjack Authorize API, as well as the get status
    and change status methods.
    
    Currently just testing the Authorize API and transaction deletion via the
    signals we have hooked up to Transaction.delete() that call
    Transaction.delete_transaction() to remove the transaction from
    Skipjack.
    
    """
    def setUp(self):
        """Avoding sending real requests to Skipjack."""
        settings.DEBUG = True
        settings.SKIPJACK_DEBUG = True
        self.old_debug = settings.DEBUG
        self.old_skipjack_debug = settings.SKIPJACK_DEBUG
        try:
            self.email = settings.ADMINS[0][1]
        except IndexError:
            self.email = 'noone@nowhere.com'
        # Complate Data
        self.base_data = [
            # Billing Information
            ('SJName', 'John Doe'),                 # Required.
            ('StreetAddress', '123 Demo Street'),   # Required.
            ('City', 'Cincinatti'),                 # Required.
            ('State', 'OH'),                        # Required.
            ('ZipCode', '12345'),                   # Required.
            ('Country', 'US'),                      # Optional (probably).
            ('Email', self.email),                  # Required.
            # Shipping Information
            ('ShipToState', 'OH'),                  # Required.
            ('ShipToZipCode', '12345'),             # Optional Level 1.
            ('ShipToCountry', 'US'),                # Optional Level 1.
            ('ShipToPhone', '9024319977'),          # Required.
            # Transaction
            ('OrderNumber', RandomOrderNumber()),   # Required.
            ('TransactionAmount', '100.00'),        # Required.
            # OrderString: SKU~Description~UnitPrice~Qty~Taxable~OverrideAVS||
            # No "~`!@#$%^&*()_-+= can be used according to Skipjack...
            ('OrderString', 'SKU~Description~50.00~2~N~||'),
            # Credit Card Information
            ('AccountNumber', '4111111111111111'),  # Required.
            ('Month', '08'),                        # Required.
            ('Year', '2012'),                       # Required.
            #('CVV2', '1234')                       # Optional.
            ]
    
    def tearDown(self):
        """Return DEBUG and SKIPJACK_DEBUG to their original settings."""
        settings.DEBUG = self.old_debug
        settings.SKIPJACK_DEBUG = self.old_skipjack_debug
    
    def test_success(self):
        """Successful Transaction."""
        data = copy.copy(self.base_data)
        transaction = create_transaction(data)
        self.assertIsInstance(transaction, Transaction)
        self.assertTrue(transaction.is_approved)
        self.assertEqual(transaction.get_approved_display(), 'Approved')
        # Now remove the transaction from Skipjack...
        transaction.delete()
    
    def test_missing_fields(self):
        """Remove some required fields."""
        data = del_list_item(copy.copy(self.base_data), 'ShipToPhone')
        transaction = create_transaction(data)
        self.assertIsInstance(transaction, Transaction)
        self.assertFalse(transaction.is_approved)
        self.assertEqual(transaction.get_approved_display(), 'Declined')
        # Now remove the transaction from Skipjack...
        transaction.delete()
    
    def test_bad_cvv2(self):
        """
        Test an invalid CVV2 value.
        
        'CVV2 Value supplied is invalid'
        
        """
        data = copy.copy(self.base_data)
        data.append(('CVV2', '1234'))
        transaction = create_transaction(data)
        self.assertIsInstance(transaction, Transaction)
        self.assertFalse(transaction.is_approved)
        self.assertEqual(transaction.get_approved_display(), 'Declined')
        self.assertEqual(transaction.auth_decline_message,
                         'CVV2 Value supplied is invalid')
        # Now remove the transaction from Skipjack...
        transaction.delete()
    
    def test_bad_order_string(self):
        """
        Add a bad OrderString value.
        
        According to Skipjack, OrderString cannot contain any of the following:
        "~`!@#$%^&*()_-+=
        
        Let's test this out...
        
        Testing reveals that, actually only the & character causes failure,
        so we're just inserting that character into the mix..
        
        """
        # Add an & into the description.
        data = del_list_item(copy.copy(self.base_data), 'OrderString')
        data.append(('OrderString', '$KU~Descripti&n~50.00~2~N~||'))
        transaction = create_transaction(data)
        self.assertIsInstance(transaction, Transaction)
        self.assertFalse(transaction.is_approved)
        self.assertEqual(transaction.get_approved_display(), 'Declined')
        self.assertEqual(transaction.get_return_code_display(),
                         'Order string incorrect')
        # Removing expected parts of the order string...
        data.append(('OrderString', 'Two pipes, no tilde...||'))
        transaction = create_transaction(data)
        self.assertEqual(transaction.get_return_code_display(),
                         'Order string incorrect')
        data = del_list_item(data, 'OrderString')
        data.append(('OrderString', 'One pipe...|'))
        transaction = create_transaction(data)
        self.assertEqual(transaction.get_return_code_display(),
                         'Order string incorrect')
        data = del_list_item(data, 'OrderString')
        data.append(('OrderString', 'Ending with 1 tilde, 2 pipes is ok...~||'))
        transaction = create_transaction(data)
        self.assertEqual(transaction.get_return_code_display(), 'Success')
    
    def test_amount_too_high(self):
        """
        Test an amount that is too large for the test card.
        
        """
        data = del_list_item(copy.copy(self.base_data), 'TransactionAmount')
        data.append(('TransactionAmount', '5000.00'))
        transaction = create_transaction(data)
        self.assertIsInstance(transaction, Transaction)
        self.assertFalse(transaction.is_approved)
        self.assertEqual(transaction.get_approved_display(), 'Declined')
        self.assertEqual(transaction.auth_decline_message,
                         'Authorization failed, card declined.')
        # Now remove the transaction from Skipjack...
        transaction.delete()
    