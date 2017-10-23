[![Build Status](https://travis-ci.org/snudler6/time-travel.svg?branch=master)](https://travis-ci.org/snudler6/time-travel) [![Build status](https://ci.appveyor.com/api/projects/status/y13ewnvmj0muoapf/branch/master?svg=true)](https://ci.appveyor.com/project/snudler6/time-travel/branch/master) [![Documentation Status](https://readthedocs.org/projects/time-travel/badge/?version=latest)](http://time-travel.readthedocs.io/en/latest/?badge=latest)


# time-travel - time and I/O mocking library
**time-travel** is a python library that allows users to write deterministic
tests for time sensitive and I/O intensive code.

When loaded, the library mocks modules that access the machine's time
(e.g. `time`, `datetime`) and I/O event handlers (e.g. `poll`, `select`) and
replaces them with an internal event-pool implementation that lets the user
choose when time moves forward and which I/O event will happen next.

**time-travel** supports python 2.7, 3.4, 3.5, 3.6 and pypy on both Linux
and Windows.

## Quick start

### install

```pip install time_travel```

### Usage

With `time-travel`, the following piece of code runs instantaneously:

```python
from time_travel import TimeTravel

with TimeTravel() as tt:
    tt.clock.time = 100000
    assert time.time() == 100000
    time.sleep(200)
    assert time.time() == 100200
```

`time-travel` also allows you to define I/O event that will "happen"
during the program:

```python
with TimeTravel() as t:
    sock = socket.socket()
    t.add_future_event(time_from_now=2, sock, t.event_types.select.WRITE)

    now = t.clock.time
    assert select.select([], [sock], []) == ([], [sock], [])
    assert time.time() == now + 2
```

For detailed information and usage examples, see the
[full documentation](http://time-travel.readthedocs.io/en/latest/).

# Links

[Full documentation](http://time-travel.readthedocs.io/en/latest/)

[PyPI project page](https://pypi.python.org/pypi/time_travel)
