Implementation Details
======================

Internally, ``time-travel`` has 2 main objects: a ``clock``, and
an ``event pool``.

The Clock
---------

The clock is an object that holds the current time (as a float), and has
``listeners`` that are registered to it.
Whenever the time changes, the listeners's callback is called with the new
time so they can react to it.

The Event Pool
--------------

The event pool keeps a set of events for different file descriptors, in
different timestamps. The pool's job is to keep those events and to retrieve
them for different patchers.

.. todo::

   Document the patcher's interface with the pool (#50).

Writing a Patcher
-----------------

Lets create a new patcher that patches the ``time`` module.
Your patcher should inherit from ``BasePatcher`` and implement 2 methods:

* `get_patched_module` should return the actual module being patched by
  the patcher.
* `get_patch_actions` should return a list containing 3-tuples with the
  following information: `(object_name, the_real_object, fake_object)`

.. code-block:: python

   import time
   from time_travel.patchers.basic_patcher import BasicPatcher

   class MyNewPatcher(BasicPatcher):
       def get_patched_module(self):
           return time

       def get_patch_actions(self):
           return ('time.time', time.time, self._mock_time)

       def _mock_time(self):
           return 4  # Decided by a fair dice roll.

Adding the patcher to time-travel
---------------------------------

``time-travel`` uses entry points to add external patchers to it.
For example let's imagine that our ``MyNewPatcher`` class is located in a file
named ``my_new_patcher.py``. In order to add the new patcher to ``time-travel``
just add the new class to the `time_travel.patchers` entry point in
``setup.py``:

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

Event Types Hooks
-----------------

If you need to hook event types to ``TimeTravel.event_types`` (like
:py:func:`select.select()` does) your patcher should override 2 methods:

* `get_events_namespace` should return a string that identifies the "namespace"
  of the event types. For example, if this returns "foo", your events will be
  registered under ``TimeTravel.event_types.foo``.
* `get_event_types` should return an ``Enum`` object that contains the events.

For example:

.. code-block:: python

   from time_travel.patchers.basic_patcher import BasicPatcher

   class MyNewPatcher(BasicPatcher):
       @staticmethod
       def get_events_namespace():
           return "foo"

       @staticmethod
       def get_event_types():
           return Enum("events", ['READ', 'WRITE'])
