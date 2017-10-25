Implementation Details
======================

Internally, ``time-travel`` has 2 main objects - a ``clock``, and an
``event pool``.

The Clock
---------

The clock is an object that holds the current time (as a float), and has
``listeners`` that are registered to it.
Whenever the time changes, the listeners's callback is called with the new
time so they can react to it.

The Event Pool
--------------

The event pool keeps a set of events for different file descriptors, in
different timestamps.
The pool's job is to keep those events, and to retrieve them for different
patchers. For example, if

When entering the TimeTravel context manager a set of ``patchers`` is activated.
Each ``patcher`` is a class that mocks the implementation of some time or I/O
related python module

The initial time within the time travel context manager is set to
86,400.0 seconds in order to support windows (this is the lowest acceptable 
value by the OS). This value is exported via ``time_travel.MIN_START_TIME``.

In order to improve TimeTravel's performance, you can give it the names of 
modules you want to patch (in list, tuple or single name). 
If you want to patch the current module, you can use the local 
variable `__name__`.

Adding patchers to time-travel
------------------------------

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
