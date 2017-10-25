Tutorial
========

Why should I use time-travel?
-----------------------------

Writing good tests can sometimes be a bit tricky, especially when you are
testing code that uses a lot of I/O and has hard timing constraints.

The naïve approach for testing such code is to actually wait for the time to
pass. This is bad. Horribly bad. Why?

1. Tests shouldn't take long.
2. Time is not accurate. When you wait for timeouts, there's always a threshold.
   If your code expects **exactly** 5 seconds to pass, there's no guarantee that
   ``time.sleep`` will wait exactly that long.

If you rely on timing in your tests - your build **will never be reliable**.

How does it work?
-----------------

When loaded, the library mocks modules that access the machine's time
(e.g. ``time``, ``datetime``) and I/O event handlers (e.g. ``poll``, ``select``)
and replaces them with an internal event-pool implementation that lets the user
choose when time moves forward and which I/O event will happen next.

The TimeTravel Context Manager
------------------------------

.. autoclass:: time_travel.TimeTravel

.. note::

   The initial time for the clock is set to `86,400` seconds since epoc.
   This is because Windows does not support any lower values. Sorry UNIX users!

Performance
^^^^^^^^^^^

The way the context manager works is that it changes references to patched
objects in loaded modules. By default ``time-travel`` searches through
**every loaded module** in ``sys.modules``. **This takes around 2 seconds**.

**Wait!! Don't leave yet!! We managed to solve this!!!**

To minimize search time, ``time_travel.TimeTravel`` gets a keyword argument
named ``modules_to_patch``, which is a list of module names to search in.

For example, let's say you're testing a module named `foobar`:

.. code-block:: python

   import foobar

   with TimeTravel(modules_to_patch=['foobar']) as t:
       foobar.dostuff()

This will reduce the replace time to the bare minimum.

.. note::

   When the default search mehtod is used (without the ``modules_to_patch``
   argument) the following modules are skipped and not patched:

   - ``pytest``
   - ``unittest``
   - ``mock``
   - ``threading``

Moving Through Time
^^^^^^^^^^^^^^^^^^^

.. function:: time.time()

   Return the time stored in ``time-travel``'s internal clock.

.. function:: time.sleep(secs)

   Move ``time-travel``'s internal clock forward by `secs` seconds.

.. function:: datetime.date.today()

   Return a ``datetime.date`` object initialized to the day that
   ``time-travel``'s internal clock is set to.

.. function:: datetime.datetime.today()

   Return a ``datetime.datetime`` object initialized to the day that
   ``time-travel``'s internal clock is set to.

.. function:: datetime.datetime.now()

   Return a ``datetime.datetime`` object initialized to the time that
   ``time-travel``'s internal clock is set to.

.. function:: datetime.datetime.utcnow()

   Return a ``datetime.datetime`` object initialized to the time that
   ``time-travel``'s internal clock is set to (timezone naive).

Faking I/O Events
^^^^^^^^^^^^^^^^^

To mock I/O events, the user must tell ``time-travel`` which event will happen,
for which file descriptor, and when. For that we have:

.. automethod:: time_travel.TimeTravel.add_future_event

For example:

.. code-block:: python

   with TimeTravel() as t:
       sock = socket.socket()
       t.add_future_event(2, sock, EVENT)

.. note::

   ``EVENT`` is implementation specific for every event handler (``select``,
   ``poll``, etc.) and will be described in the corresponding handler's
   documentation.

.. function:: select.select(rlist, wlist, xlist, timeout=None)

   Mimics the behaviour of ``select.select``.

   ``select`` has no event types, it uses positional lists in order to
   distinguish between `read-ready`, `write-ready` and `exception`.
   :py:func:`TimeTravel.add_future_event` requires an event type, so the
   following consts are provided:

   - ``TimeTravel.event_types.select.READ``
   - ``TimeTravel.event_types.select.WRITE``
   - ``TimeTravel.event_types.select.EXCEPTIONAL``

   The mock returns the first event(s) that expire in the event pool and moves
   time forward to that point in time. For example, if the user added 2 events:

   .. code-block:: python

      t.add_future_event(1, sock1, t.event_types.select.READ)
      t.add_future_event(2, sock2, t.event_types.select.READ)

   Calling ``select.select([sock1, sock2], [], [])`` will return an rlist
   containing only ``sock1`` and the time will move forward by 1 second.

.. function:: select.poll()

   Return a ``MockPollObject`` that behaves exactly like the real ``Poll``
   object.

   .. note::

      This patcher is not supported on Windows.

   .. autoclass:: time_travel.patchers.poll_patcher.MockPollObject
      :members:

   The `event type` supplied to :py:func:`TimeTravel.add_future_event` is the
   event mask that is required by `poll.poll()` (``select.POLLIN``,
   ``select.POLLOUT``, etc.).
