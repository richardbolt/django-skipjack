"""Admin definitions for the Skipjack usage in Django's admin site."""
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.util import get_deleted_objects
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import router
from django.template.response import TemplateResponse
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _

from skipjack.models import Transaction, TransactionError

"""
#--------------------------------------------
# SimpleListFilter is available in Django 1.4+
from django.contrib.admin import SimpleListFilter
class IsApprovedListFilter(SimpleListFilter):
    title = _('Approved transactions')
    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'is_approved'

    def lookups(self, request, model_admin):
        "Filter based on our is_approved method."
        return (
            (True, _('yes')),
            (False, _('no')),
        )

    def queryset(self, request, queryset):
        "Filter based on the is_approved logic."
        return queryset.filter(approved='1').exclude(auth_code='',
                                                     auth_response_code='')
#--------------------------------------------
"""

class TransactionAdmin(admin.ModelAdmin):
    """Admin model for the Transaction model."""
    actions = ['delete_transactions', 'refund_transactions',
               'settle_transactions', 'update_transactions']
    search_fields = ('transaction_id', 'amount', 'order_number', 'auth_code',
                     'auth_response_code')
    date_hierarchy = 'creation_date'
    list_display = ('transaction_id',
                    'order_number',
                    'approved',
                    'is_approved',
                    'auth_code',
                    'creation_date',
                    'current_status',
                    'pending_status',
                    'amount',
                    'is_live',
                    'return_code')
    list_filter = ('is_live', 'approved', 'creation_date', 'current_status',
                   'pending_status')
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
                       'is_live',
                       'creation_date',
                       'mod_date',
                       'status_text',
                       'status_date',
                       'current_status',
                       'pending_status')
    fieldsets = (
        (None, {
            'fields': (('transaction_id', 'return_code', 'is_live'),
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
            'fields' : (('status_text', 'status_date'),
                        ('current_status', 'pending_status'))
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
    
    def get_actions(self, request):
        """Don't use the generic delete_selected action."""
        actions = super(TransactionAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    
    def delete_transactions(self, request, queryset):
        """
        Delete transactions, ensuring we delete them from Skipjack.
        
        Offers up a confirmation page.
        
        Basically ripped from `django.contrib.admin.actions.delete_selected`.
        
        Supports the standard Django admin and the Grappelli look and feel
        with templates for both provided and selected automatically.
        
        """
        opts = self.model._meta
        app_label = opts.app_label
        
        # Check that the user has the delete permission.
        if not self.has_delete_permission(request):
            raise PermissionDenied
        
        using = router.db_for_write(self.model)
        
        # Populate deletable_objects, a data structure of all related objects
        # that will also be deleted.
        deletable_objects, perms_needed, protected = get_deleted_objects(
            queryset, opts, request.user, self.admin_site, using)
        
        # The user has already confirmed the deletion.
        # Do the deletion and return None to display the change list view again.
        if request.POST.get('post'):
            rows_updated = 0
            for obj in queryset:
                obj_display = force_unicode(obj)
                self.log_deletion(request, obj, obj_display)
                # NB: obj.delete() calls obj.delete_transaction()
                # which deletes the Transaction from Skipjack if possible.
                try:
                    obj.delete()
                    rows_updated += 1
                except TransactionError:
                    messages.error(request,
                                   "Transaction %s could not be deleted." %
                                   obj.transaction_id)
            # Send a success message.
            if rows_updated > 0:
                if rows_updated == 1:
                    message_bit = "1 transaction was"
                else:
                    message_bit = "%s transactions were" % rows_updated
                messages.success(request, "%s successfully deleted." %
                                                                    message_bit)
            
            # Return None to display the change list page again.
            return None
        
        if len(queryset) == 1:
            objects_name = force_unicode(opts.verbose_name)
        else:
            objects_name = force_unicode(opts.verbose_name_plural)
        
        if perms_needed or protected:
            title = _("Cannot delete %(name)s") % {"name": objects_name}
        else:
            title = _("Are you sure?")
        
        context = {
            "title": title,
            "objects_name": objects_name,
            "deletable_objects": [deletable_objects],
            'queryset': queryset,
            "perms_lacking": perms_needed,
            "protected": protected,
            "opts": opts,
            "app_label": app_label,
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
        }
        
        # Display the confirmation page
        if "grappelli" in settings.INSTALLED_APPS:
            template_list = [
                "admin/%s/%s/delete_selected_transactions.grp.html" % (
                                    app_label, opts.object_name.lower()),
                "admin/%s/delete_selected_transactions.grp.html" % app_label,
                "admin/delete_selected_transactions.grp.html"]
        else:
            template_list = [
                "admin/%s/%s/delete_selected_transactions.html" % (
                                    app_label, opts.object_name.lower()),
                "admin/%s/delete_selected_transactions.html" % app_label,
                "admin/delete_selected_transactions.html"]
        return TemplateResponse(request, template_list, context,
                                current_app=self.admin_site.name)
    delete_transactions.short_description = "Delete selected transactions..."
    
    def settle_transactions(self, request, queryset):
        """Settle (Charge) selected transactions with Skipjack."""
        rows_updated = 0
        for obj in queryset:
            try:
                obj.settle()
                self.log_change(request, obj, 'Settled %s' % force_unicode(obj))
                rows_updated += 1
            except TransactionError:
                messages.error(request,
                               "Transaction %s could not be settled." %
                               obj.transaction_id)
                obj.update_status()
        # Send a success message.
        if rows_updated > 0:
            if rows_updated == 1:
                message_bit = "1 transaction was"
            else:
                message_bit = "%s transactions were" % rows_updated
            messages.success(request, "%s successfully added to the " \
                                      "settlement que." % message_bit)
    settle_transactions.short_description = "Settle selected transactions"
    
    def refund_transactions(self, request, queryset):
        """Fully refund selected transactions with Skipjack."""
        opts = self.model._meta
        app_label = opts.app_label
        
        # Check that the user has the change permission.
        if not self.has_change_permission(request):
            raise PermissionDenied
        
        # The user has already confirmed the refunds.
        # Do the refunds and return None to display the change list view again.
        if request.POST.get('post'):
            rows_updated = 0
            for obj in queryset:
                try:
                    obj.refund()
                    self.log_change(request, obj, 'Refunded %s' %
                                                            force_unicode(obj))
                    rows_updated += 1
                except TransactionError:
                    messages.error(request,
                                   "Transaction %s could not be refunded." %
                                   obj.transaction_id)
                    obj.update_status()
            # Send a success message.
            if rows_updated > 0:
                if rows_updated == 1:
                    message_bit = "1 transaction was"
                else:
                    message_bit = "%s transactions were" % rows_updated
                messages.success(request, "%s successfully refunded." %
                                                            message_bit)
            
            
            # Return None to display the change list page again.
            return None
        
        if len(queryset) == 1:
            objects_name = force_unicode(opts.verbose_name)
        else:
            objects_name = force_unicode(opts.verbose_name_plural)
        
        title = _("Are you sure?")
        
        change_url_name = '%s:%s_%s_change' % (self.admin_site.name,
                                               opts.app_label,
                                               opts.object_name.lower())
        
        context = {
            "title": title,
            "objects_name": objects_name,
            "queryset": queryset,
            "opts": opts,
            "app_label": app_label,
            "change_url_name": change_url_name,
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
        }
        
        # Display the confirmation page
        if "grappelli" in settings.INSTALLED_APPS:
            template_list = [
                "admin/%s/%s/refund_selected_transactions.grp.html" % (
                                    app_label, opts.object_name.lower()),
                "admin/%s/refund_selected_transactions.grp.html" % app_label,
                "admin/refund_selected_transactions.grp.html"]
        else:
            template_list = [
                "admin/%s/%s/refund_selected_transactions.html" % (
                                    app_label, opts.object_name.lower()),
                "admin/%s/refund_selected_transactions.html" % app_label,
                "admin/refund_selected_transactions.html"]
        return TemplateResponse(request, template_list, context,
                                current_app=self.admin_site.name)
    refund_transactions.short_description = "Refund selected transactions..."
    
    
    def update_transactions(self, request, queryset):
        """Update the status of selected transactions with Skipjack."""
        rows_updated = 0
        for obj in queryset:
            try:
                obj.update_status()
                self.log_change(request, obj, 'Updated %s' % force_unicode(obj))
                rows_updated += 1
            except TransactionError:
                messages.error(request,
                               "Transaction %s could not be updated." %
                               obj.transaction_id)
        # Send a success message.
        if rows_updated > 0:
            if rows_updated == 1:
                message_bit = "1 transaction was"
            else:
                message_bit = "%s transactions were" % rows_updated
            messages.success(request, "%s successfully updated." % message_bit)
    update_transactions.short_description = "Update status of selected transactions"

admin.site.register(Transaction, TransactionAdmin)
