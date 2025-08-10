.. robinhood-client documentation master file, created by
   sphinx-quickstart on Sun Aug 10 08:16:02 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Robinhood Client |release|
==============================

An unofficial API client that provides a Python interface for the Robinhood API that the official Robinhood App uses.

This is a pure python interface and it requires Python 3. The purpose
of this library is to allow people to programmatically interact with their Robinhood account.

.. warning::

  These functions make real time calls to your Robinhood account. Unlike in the app, there are
  no warnings when you are about to buy, sell, or cancel an order. It is up to **YOU** to use
  these commands responsibly.

User Guide
==========

Below is the table of contents for Robinhood Client. Use it to find example code or
to scroll through the list of all the callable functions.

.. toctree::
   :maxdepth: 2

   install
   quickstart
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`