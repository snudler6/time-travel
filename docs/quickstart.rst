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
