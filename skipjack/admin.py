from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from skipjack.models import Response


class ResponseAdmin(admin.ModelAdmin):
    list_display = ('transaction_id',
                    'created',
                    'return_code',
                    'auth_code',
                    'amount',
                    'avs_code',
                    'order_number',
                    'is_approved',
                    'test_request')
    list_filter = ('test_request', 'approved', 'created')
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
                       'created')
    fieldsets = (
        (None, {
            'fields': [('transaction_id', 'return_code', 'test_request')]
        }),
        (_('Totals'), {
            'classes': ('collapse', 'collapse-closed', 'wide',),
            'fields' : (('approved', 'auth_decline_message', 'auth_code',
                            'auth_response_code'),
                       )
        }),
    )
    
    def is_approved(self, object_):
        " Transform Response.is_approved into a boolean for display purposes. "
        # See: http://www.peterbe.com/plog/dislike-for-booleans-and-django-admin
        return object_.is_approved 
    is_approved.short_description = u'Approved?' 
    is_approved.boolean = True
    
    

admin.site.register(Response, ResponseAdmin)
