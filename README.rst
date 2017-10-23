.. image:: https://travis-ci.org/snudler6/time-travel.svg?branch=master
    :target: https://travis-ci.org/snudler6/time-travel

.. image:: https://ci.appveyor.com/api/projects/status/y13ewnvmj0muoapf/branch/master?svg=true
    :target: https://ci.appveyor.com/project/snudler6/time-travel/branch/master

.. image:: https://readthedocs.org/projects/time-travel/badge/?version=latest
    :target: http://time-travel.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. include:: docs/header.rst

Quick start
-----------

Install
^^^^^^^

.. code::

   pip install time_travel

Usage
^^^^^

With `time-travel`, the following piece of code runs instantaneously:

.. code-block:: python

   from time_travel import TimeTravel

   with TimeTravel() as tt:
       tt.clock.time = 100000
       assert time.time() == 100000
       time.sleep(200)
       assert time.time() == 100200

`time-travel` also allows you to define I/O event that will "happen"
during the program:

.. code-block:: python

   with TimeTravel() as t:
       sock = socket.socket()
       t.add_future_event(time_from_now=2, sock, t.event_types.select.WRITE)

       now = t.clock.time
       assert select.select([], [sock], []) == ([], [sock], [])
       assert time.time() == now + 2

For detailed information and usage examples, see the
`full documentation <http://time-travel.readthedocs.io/en/latest/>`_.

Links
=====

`Full documentation <http://time-travel.readthedocs.io/en/latest/>`_

`PyPI project page <https://pypi.python.org/pypi/time_travel>`_
