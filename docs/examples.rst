Examples
========

.. todo::

   Give better examples (#51).

Skip timeouts
^^^^^^^^^^^^^

Tests are deterministic and take no time with time travel. For example:

.. code-block:: python

   with TimeTravel():
       assert time.time() == 86400
       time.sleep(200)
       assert time.time() == 86600

.. code-block:: python

   with TimeTravel(modules_to_patch=__name__):
       assert datetime.today() == datetime.fromtimestamp(86400)
       time.sleep(250)
       assert datetime.today() == datetime.fromtimestamp(86650)

.. code-block:: python

   import module1
   import module2

   with TimeTravel(modules_to_patch=['module1', 'module2']) as time_machine:
       time_machine.set_time(100000)
       module1.very_long_method()
       module2.time_sensitive_method()

Patching I/O events modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^

With ``time-travel`` you can fake future events for I/O modules:

.. code-block:: python

   with TimeTravel() as t:
       sock = socket.socket()
       t.add_future_event(2, sock, t.event_types.select.WRITE)
    
       now = t.clock.time
       assert select.select([], [sock], []) == ([], [sock], [])
       assert time.time() == now + 2
       assert datetime_cls.today() == datetime_cls.fromtimestamp(now + 2)

Or using ``poll`` (for supported platforms only):

.. code-block:: python

   with TimeTravel() as t:
       sock = socket.socket()
       t.add_future_event(2, sock, select.POLLIN)

       poll = select.poll()
       poll.register(sock, select.POLLIN | select.POLLOUT)
    
       now = t.clock.time
       assert poll.poll() == [(sock, select.POLLIN)]
       assert time.time() == now + 2
