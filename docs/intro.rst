.. _intro:

Introduction
============

Django-Skipjack is an implementation of the AuthorizeAPI for the `Skipjack`_
payment gateway built on the `Django Web Framework`_.

It consists of a resuable Django app, `skipjack`, which you can use in your
project.

Initial development was focused around the needs of Texmate, Inc, who use
Skipjack for payment processing, and uses ideas borrowed from
`github.com/zen4ever/django-authorizenet/`_.

Features
--------

* AuthorizeAPI support.
* Get Transaction Status support.
* Change Transaction Status support.
* A `Transaction` model created with an AuthorizeAPI request featuring the above
  get and change status support.


Python Versions
---------------

At this time, the following Python versions are supported:

 * Python 2.5
 * Python 2.6
 * Python 2.7


.. _djangosupport:

Django Versions
---------------

At this time, the following Django versions are supported:

 * Django 1.2
 * Django 1.3



.. _`Django Web Framework`: https://www.djangoproject.com/
.. _`Skipjack`: http://www.skipjack.com/
.. _`github.com/zen4ever/django-authorizenet/`: https://github.com/zen4ever/django-authorizenet/