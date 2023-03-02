.. image:: https://travis-ci.org/EtsBiz4africa/ofxstatement-paypal.svg?branch=master
    :target: https://travis-ci.org/EtsBiz4africa/ofxstatement-paypal

ofxstatement-paypal
===================

This is a collection of parsers for proprietary statement formats, produced by
`PayPal`_. It parses ``*.csv`` file exported from the site.

It is a plugin for `ofxstatement`_.

.. _PayPal: https://www.paypal.com
.. _ofxstatement: https://github.com/kedder/ofxstatement

Configuration
=============

PayPal exports data for all currencies in one file. This means you must define different configurations for different
currencies. See below for examples.

It worth mentioning that there is ``analyze`` option that enables simple analyzing that modifies memo in attempt
to make it more relevant e.g. it picks ``Item Title`` for any steam purchases:

``WWW.Steampowered.com`` -> ``WWW.Steampowered.com / Hero Siege``

It is completely optional and up to you.

Locale
======

You can configure exact locale and encodings to use during parsing. Here is example how to configure both of them
with the default configuration you always have.

.. code-block::

    [default]
    plugin = paypal
    encoding = iso8859-1

    [paypal]
    plugin = paypal
    encoding = iso8859-1
    locale = sv_SE
    ...

Example
=======

.. code-block::

    [paypal:sek]
    plugin = paypal
    account_id = john.doe@gmail.com/SEK
    currency = SEK
    analyze = 1

    [paypal:eur]
    plugin = paypal
    account_id = john.doe@gmail.com/EUR
    currency = EUR
    analyze = 1

    [paypal:usd]
    plugin = paypal
    account_id = john.doe@gmail.com/USD
    currency = USD
    analyze = 1
