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
