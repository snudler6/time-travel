.. image:: https://travis-ci.org/snudler6/time-travel.svg?branch=master
    :target: https://travis-ci.org/snudler6/time-travel

.. image:: https://ci.appveyor.com/api/projects/status/y13ewnvmj0muoapf/branch/master?svg=true
    :target: https://ci.appveyor.com/project/snudler6/time-travel/branch/master

.. image:: https://readthedocs.org/projects/time-travel/badge/?version=latest
    :target: http://time-travel.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/pypi/pyversions/time-travel.svg
    :target: https://pypi.org/project/time-travel

time-travel - time and I/O mocking library
==========================================

**time-travel** is a python library that helps users write deterministic
tests for time sensitive and I/O intensive code.

**time-travel** supports python 2.7, 3.4, 3.5, 3.6 and pypy2 on both Linux
and Windows.

Install
-------

.. code:: bash

   $ pip install time_travel

Testing Time Sensitive Code
---------------------------

Imagine testing a state machine that times out after some time passes.
One way to test it would be:

.. code-block:: python

   def test_state_timeout():
       sm.handle_event(event=...)
       time.sleep(5)
       sm.handle_event(event=...)
       assert sm.state == TIMEOUT

This is bad for several reasons:

* **Your test takes 5 seconds to run**. That's a no-no.
* ``time.sleep()`` promises that the process will sleep ``x`` seconds
  **at most**. This test might fail randomly, depending on how sensitive your
  state machine is.

There's nothing worse than a heisenbuild (well, perhaps a **SLOW** heisenbuild).
Here's a **better** way to do this using ``time-travel``:

.. code-block:: python

   def test_state_timeout():
       with TimeTravel() as tt:
           sm.handle_event(event=...)
           tt.clock.time += 5
           sm.handle_event(event=...)
           assert sm.state == TIMEOUT

When the ``handle_event`` method is called it will probably check the time
using one of ``time`` or ``datetime`` modules. These modules are patched by
``time-travel`` and return the value stored in ``TimeTravel.clock.time``.

From now on, your time sensitive tests will run faster, accurately, and your
build will be consistent.

Testing I/O Code
----------------

``time-travel`` also mocks I/O event interfaces such as ``select`` and ``poll``.

Testing code that uses ``select`` is easy - you just inject a real socket object
and send data to it from your test code. But what about timeouts? Testing
behaviour that occurs on timeout forces you to actually **wait**! That's bananas!

Here's how you'd do it with ``time-travel``:

.. code-block:: python

   def test_select_timeout():
       with TimeTravel() as tt:
           sock = socket.socket()
           tt.add_future_event(2, sock, tt.event_types.select.WRITE)
           start = time.time()
           assert select.select([sock], [sock], []) == ([], [sock], [])  # This will be satisfied after "2 seconds"
           assert time.time() == start + 2  # You see? 2 seconds!
           assert select.select([sock], [sock], [], 100) == ([], [], [])  # This is the "timeout"
           assert time.time() == start + 2 + 100

Once again, this code will run instantly.

Oh yes, ``sock`` doesn't even have to be a socket object :)


For detailed information and usage examples, see the
`full documentation <http://time-travel.readthedocs.io/en/latest/>`_. You know
you want to.

Links
=====

`Full documentation <http://time-travel.readthedocs.io/en/latest/>`_

`PyPI project page <https://pypi.python.org/pypi/time_travel>`_
