
Advanced Usage
==============

----


Making Custom Get and Post Requests
-----------------------------------

Parakeet depends on Requests which you are free to call and use yourself, or you could
use it within the framework by using :func:`parakeet.helper.request_get`, :func:`parakeet.helper.request_post`,
:func:`parakeet.helper.request_document`, and :func:`parakeet.helper.request_delete`. For example, if you wanted to make your own
get request to the option instruments API endpoint in order to get all calls you would type:

>>> url = 'https://api.robinhood.com/options/instruments/'
>>> payload = { 'type' : 'call'}
>>> parakeet.request_get(url,'regular',payload)

Robinhood returns most data in the form::

{ 'previous' : None, 'results' : [], 'next' : None}

where 'results' is either a dictionary or a list of dictionaries. However, sometimes
Robinhood returns the data in a different format. To compensate for this, I added
the **dataType** parameter which defaults to return the entire dictionary listed above.
There are four possible values for **dataType** and their uses are:

>>> parakeet.robinhood.request_get(url,'regular')    # For when you want
>>>                                            # the whole dictionary
>>>                                            # to view 'next' or
>>>                                            # 'previous' values.
>>>
>>> parakeet.robinhood.request_get(url,'results')    # For when results contains a
>>>                                            # list or single dictionary.
>>>
>>> parakeet.robinhood.request_get(url,'pagination') # For when results contains a
>>>                                            # list, but you also want to
>>>                                            # append any information in
>>>                                            # 'next' to the list.
>>>
>>> parakeet.robinhood.request_get(url,'indexzero')  # For when results is a list
>>>                                            # of only one entry.

Also keep in mind that the results from the Robinhood API have been decoded using ``.json()``.
There are instances where the user does not want to decode the results (such as retrieving documents), so
I added the :func:`parakeet.helper.request_document` function, which will always return the raw data,
so there is no **dataType** parameter. :func:`parakeet.helper.request_post` is similar in that it only
takes a url and payload parameter.
