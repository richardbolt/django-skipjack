"""
Signals for Skipjack payments.

You can use these in your app as generic payment signals.

"""
from django.dispatch import Signal

__all__ = ['payment_was_successful',
           'payment_was_flagged']


payment_was_successful = Signal()
payment_was_flagged = Signal()
