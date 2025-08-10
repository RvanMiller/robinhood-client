
API Reference
=======================

.. note::
  Simply use ``robinhood_client.function`` for all functions.

  Even though the functions are written as ``robinhood_client.module.function``, the module
  name is unimportant when calling a function. 

Sending Requests to API
-----------------------

.. automodule:: robinhood_client.helper
   :members: request_get,request_post,request_delete,request_document

Logging In and Out
------------------

.. automodule:: robinhood_client.authentication
   :members: login, logout, generate_device_token

Loading Profiles
------------------

.. automodule:: robinhood_client.profiles
   :members:

Getting Stock Information
-------------------------


.. automodule:: robinhood_client.stocks
   :members:

Getting Option Information
--------------------------


.. automodule:: robinhood_client.options
   :members:

Getting Market Information
--------------------------


.. automodule:: robinhood_client.markets
   :members:

Getting Positions and Account Information
-----------------------------------------


.. automodule:: robinhood_client.account
   :members:

Placing and Cancelling Orders
-----------------------------


.. automodule:: robinhood_client.orders
   :members:

Getting Crypto Information
--------------------------


.. automodule:: robinhood_client.crypto
   :members:

Export Information
--------------------------


.. automodule:: robinhood_client.export
   :members:
