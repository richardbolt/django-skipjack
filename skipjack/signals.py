"""
Signals for Skipjack payments.

You can use these in your app as generic payment signals.

"""
from django.dispatch import Signal

__all__ = ['payment_was_successful',
           'payment_was_flagged',
           'payment_status_changed']


payment_was_successful = Signal(providing_args=['instance'])
payment_was_flagged = Signal(providing_args=['instance'])

# Usage: payment_status_changed.send(sender=Transaction, instance=trans)
payment_status_changed = Signal(providing_args=['instance'])
