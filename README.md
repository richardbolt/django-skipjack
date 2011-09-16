django-skipjack
===============

*Django integration with [Skipjack](http://www.skipjack.com/), a payment gateway.*

Includes the AuthorizeAPI implementation for payment submission useful in
shopping cart integration and integration into custom CRM payment solutions.


Quickstart
----------

Below is a quick example to help you get started processing with Skipjack.
The ``response`` variable returned from the ``create_transaction()`` is a
``Transaction`` object as defined in ``skipjack/models.py``.
    
    
In your ``settings.py``, you'll want the following settings customized to match
whatever your Skipjack data happens to be:
    
    SKIPJACK_DEBUG = DEBUG
    SKIPJACK_SERIAL_NUMBER  ='000111222333'
    SKIPJACK_DEVELOPER_SERIAL_NUMBER = 'ABC123456789'
    
    If you want to use the reports, you'll also need these settings:
    
    SKIPJACK_LOGIN_SERIAL_NUMBER = '000123456789'
    SKIPJACK_LOGIN_USERNAME = 'MontyInc'
    SKIPJACK_LOGIN_PASSWORD = 'Python'
    
    
Basic usage:
    
    from skipjack.utils import create_transaction
    
    final_data = {
        # Billing Information
        'SJName': 'John Doe',
        'StreetAddress': '123 Demo Street',
        'City': 'Cincinatti',
        'State': 'OH',
        'ZipCode': '12345',
        'Country': 'US',            # Optional (probably).
        'Email': 'jd@skipjack.com',
        # Shipping Information
        'ShipToState': 'OH',
        'ShipToZipCode': '12345',   # Optional Level 1.
        'ShipToCountry': 'US',      # Optional Level 1.
        'ShipToPhone': '9024319977',
        # Transaction
        'OrderNumber': '12345',
        'TransactionAmount': '150.00',
        # OrderString: SKU~Description~UnitPrice~Qty~Taxable~OverrideAVS||
        # No "~`!@#$%^&*()_-+= can be used...
        'OrderString': 'SKU~Description~75.00~2~N~||',
        # Credit Card Information
        'AccountNumber': '4111111111111111',
        'Month': '08',
        'Year': '2012',
        'CVV2': '123'               # Optional.
        }
    
    transaction = create_transaction(final_data)

- - -

Original code ideas borrowed from:
[github.com/zen4ever/django-authorizenet/](https://github.com/zen4ever/django-authorizenet/)
