django-skipjack
===============

*Django integration with [Skipjack](http://www.skipjack.com/), a payment gateway.*

Includes the AuthorizeAPI implementation for payment submission useful in
shopping cart integration and integration into custom CRM payment solutions.


Quickstart
----------

Below is a quick example to help you get started processing with Skipjack.
The ``response`` variable returned from the ``create_response()`` is a
``Response`` object as defined in ``skipjack/models.py``.

    from skipjack.utils import create_response
    
    final_data = (
        # Using a tuples to ensure order of the urlencoded string.
        # This apparently matters a great deal to Skipjack.
        ('SerialNumber', '000111222333'),       # Required.
        ('DeveloperSerialNumber', 'ABC123456789'),
        # Billing Information
        ('SJName', 'John Doe'),                 # Required.
        ('StreetAddress', '123 Demo Street'),   # Required.
        ('City', 'Cincinatti'),                 # Required.
        ('State', 'OH'),                        # Required.
        ('ZipCode', '12345'),                   # Required.
        ('Country', 'US'),                      # Optional (probably).
        ('Email', 'jd@skipjack.com'),           # Required.
        # Shipping Information
        ('ShipToState', 'OH'),                  # Required.
        ('ShipToZipCode', '12345'),             # Optional Level 1.
        ('ShipToCountry', 'US'),                # Optional Level 1.
        ('ShipToPhone', '9024319977'),          # Required.
        # Transaction
        ('OrderNumber', '12345'),               # Required.
        ('TransactionAmount', '150.00'),        # Required.
        # OrderString: SKU~Description~UnitPrice~Qty~Taxable~OverrideAVS||
        # No "~`!@#$%^&*()_-+= can be used...
        ('OrderString', 'SKU~Description~75.00~2~N~||'),
        # Credit Card Information
        ('AccountNumber', '4111111111111111'),  # Required.
        ('Month', '08'),                        # Required.
        ('Year', '2012'),                       # Required.
        ('CVV2', '1234')                        # Optional.
        )
    
    response = create_response(final_data)

- - -

Original code ideas borrowed from:
[github.com/zen4ever/django-authorizenet/](https://github.com/zen4ever/django-authorizenet/)
