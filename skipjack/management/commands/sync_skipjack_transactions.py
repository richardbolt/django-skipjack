#!/usr/bin/env python
"""
Updates the status of Transactions stored in the database that have a
pending status (or no status at all).

You will want to execute this command as a regular scheduled task.

"""
import datetime
from django.core.management.base import NoArgsCommand, CommandError


class Command(NoArgsCommand):
    help = 'Sync the status of stored Skipjack Transactions.'
    
    def handle_noargs(self, **options):
        """
        Update the status (Sync) transactions that need to be synced.
        
        That would be transactions that we expect will have a change
        of status at some point...
        
        """
        from skipjack.models import Transaction, AUTHORIZED, PRE_AUTHORIZED
        num_updated = 0
        for obj in Transaction.objects.exclude(transaction_id='').filter(
                        current_status__in=(0, AUTHORIZED, PRE_AUTHORIZED)):
            obj.update_status()
            num_updated += 1
        if num_updated > 1:
            self.stdout.write('Successfully synced %d transactions.\n' %
                                                                num_updated)
        elif num_updated == 1:
            self.stdout.write('Successfully synced %d transaction.\n' %
                                                                num_updated)
