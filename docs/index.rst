time-travel - time and I/O mocking library
==========================================

**time-travel** is a python library that allows users to write deterministic
tests for time sensitive and I/O intensive code.

When loaded, the library mocks modules that access the machine's time
(e.g. `time`, `datetime`) and I/O event handlers (e.g. `poll`, `select`) and
replaces them with an internal event-pool implementation that lets the user
choose when time moves forward and which I/O event will happen next.

**time-travel** supports python 2.7, 3.4, 3.5, 3.6 and pypy on both Linux
and Windows.

.. include:: quickstart.rst

.. toctree::
   :maxdepth: 2
   :caption: Contents:


The initial time within the time travel context manager is set to
86,400.0 seconds in order to support windows (this is the lowest acceptable 
value by the OS). This value is exported via ``time_travel.MIN_START_TIME``.

In order to improve TimeTravel's performance, you can give it the names of 
modules you want to patch (in list, tuple or single name). 
If you want to patch the current module, you can use the local 
variable `__name__`.

Examples
========

Skip timeouts
-------------

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

Patching event based modules
----------------------------

Can Patch and determine future events for event based modules using select:

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

List of currently patched modules and functions
===============================================

- time.time
- time.sleep
- datetime.date.today
- datetime.datetime.today
- datetime.datetime.now
- datetime.datetime.utcnow
- select.select
- select.poll (for supported platforms only)

Add your own patches to time-travel
===================================

time-travel uses `entry points` to add external patchers to it.

For example, lets create a new patcher that patches something:

``my_new_patcher.py``:

.. code-block:: python

   from time_travel.patchers.basic_patcher import BasicPatcher

   class MyNewPatcher(BasicPatcher):
       ...

To bind the new patcher to time-travel just add the new class to the
`time_travel.patchers` entry point in your setup.py:

.. code-block:: python

   from setuptools import setup

   setup(
       ...,
       entry_points={
           'time_travel.patchers' : [
               'my_new_patcher = my_new_patcher:MyNewPatcher',
           ],
       }
   )

The patcher class should do 1 of 2 things:

1. Override and implement it's own `start` and `stop` of the patcher.
2. Inherit BasePatcher, Implement `get_patched_module` and `get_patch_actions`:

   * `get_patched_module` return the actual module patched by the patcher.
   * `get_patch_actions` return a list containing 
     `(object_name, the_real_object, fake_object)`
     where the object name is the object's name in the patched module and it
     will be replaced by the fake object.
     e.g.:

.. code-block:: python

   from time_travel.patchers import BasePatcher
   import time

   class TimePatcher(BasePatcher):
       def get_patched_module(self):
           return time
        
       def get_patch_actions(self):
           return [('time', time.time, lambda: return 0)]
