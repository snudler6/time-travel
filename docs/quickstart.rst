Quick start
===========

Install
-------

.. code:: bash

   $ pip install time_travel

Usage
-----

Here are two examples of how to use ``time-travel``. See the full tutorial for
more tips and tricks.

Mocking time-sensitive code
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   with TimeTravel():
       start = time.time()
       time.sleep(200)
       assert time.time() == start + 200

Mocking I/O code
^^^^^^^^^^^^^^^^

.. code-block:: python

   with TimeTravel() as tt:
       sock = socket.socket()
       tt.add_future_event(time_from_now=2, sock, t.event_types.select.WRITE)

       now = time.time()
       assert select.select([], [sock], []) == ([], [sock], [])
       assert time.time() == now + 2
