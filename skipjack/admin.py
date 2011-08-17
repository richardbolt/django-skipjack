"""Admin definitions for the Skipjack usage in Django's admin site."""
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from skipjack.models import Transaction


class TransactionAdmin(admin.ModelAdmin):
    """Admin model for the Transaction model."""
    search_fields = ('transaction_id', 'amount', 'order_number', 'auth_code',
                     'auth_response_code')
    date_hierarchy = 'creation_date'
    list_display = ('transaction_id',
                    'creation_date',
                    'return_code',
                    'auth_code',
                    'amount',
                    'avs_code',
                    'order_number',
                    'is_approved',
                    'test_request')
    list_filter = ('test_request', 'approved', 'creation_date')
    readonly_fields = ('transaction_id',
                       'auth_code', 
                       'amount', 
                       'auth_decline_message',
                       'avs_code',
                       'avs_message',
                       'order_number',
                       'auth_response_code',
                       'approved',
                       'cvv2_response_code',
                       'cvv2_response_message',
                       'return_code',
                       'cavv_response',
                       'test_request',
                       'creation_date',
                       'mod_date',
                       'status_text',
                       'status_date',
                       'current_status',
                       'pending_status')
    fieldsets = (
        (None, {
            'fields': (('transaction_id', 'return_code', 'test_request'),
                        'creation_date', 'amount')
        }),
        (_('Authorization'), {
            'classes': ('collapse', 'collapse-closed', 'wide',),
            'fields' : (('approved', 'auth_decline_message', 'auth_code',
                            'auth_response_code'),
                       )
        }),
        (_('Card verification value (CVV2)'), {
            'classes': ('collapse', 'collapse-closed', 'wide',),
            'fields' : [('cvv2_response_code', 'cvv2_response_message')]
        }),
        (_('Address verification service (AVS)'), {
            'classes': ('collapse', 'collapse-closed', 'wide',),
            'fields' : [('avs_code', 'avs_message',)]
        }),
        (_('Status'), {
            'classes': ('collapse', 'collapse-closed', 'wide',),
            'fields' : (('status_text', 'status_date'), ('current_status', 'pending_status'))
        }),
    )
    
    def is_approved(self, object_):
        """
        Transform Transaction.is_approved into a boolean for display purposes.
        See: http://www.peterbe.com/plog/dislike-for-booleans-and-django-admin
        
        """
        return object_.is_approved 
    is_approved.short_description = u'Approved?' 
    is_approved.boolean = True


admin.site.register(Transaction, TransactionAdmin)
