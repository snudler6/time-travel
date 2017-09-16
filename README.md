[![Build Status](https://travis-ci.org/snudler6/time-travel.svg?branch=master)](https://travis-ci.org/snudler6/time-travel)

# time-travel
python time libraries mocking

### time-travel is the fun and easy way to unit-test time sensetive modules.
### Can write determenistic test for long and even infinite time scenarios.

## Usage

`TimeTravel` is context manager patching all time modules currently patched in a single line.

In order to improve TimeTravel's performance, you can give it the names of modules you want to patch (in list, tuple or single name). If you want to patch the current module, you can use the local variable `__name__`.

### Examples

#### Skip timeouts

Tests are determenistic and take no time with time travel.

```python
with TimeTravel():  
    assert time.time() == 0
    time.sleep(3600)
    assert time.time() == 3600    
```

```python
with TimeTravel(`__name__`):
    assert datetime.today() == datetime.fromtimestamp(0)
    time.sleep(3600)
    assert datetime.today() == datetime.fromtimestamp(3600)
```

```python
import module1
import module2

with TimeTravel(patched_modules=['module1', 'module2']) as time_machine:
    time_machine.set_time(1237)
    module1.very_long_method()
    module2.time_sensative_method()
```

#### Patching event based modules

Can Patch and determine future events for event based modules using select:

```python
with TimeTravel() as t:
    event = mock.MagicMock()
    t.events_pool.add_future_event(2, event, t.events_types.select.WRITE)
    assert select.select([], [event], []) == ([], [event], [])
    assert time.time() == 2
```

Or using ``poll``:

```python
with TimeTravel() as t:
    fd = mock.MagicMock()
    t.events_pool.add_future_event(2, fd, select.POLLIN)

    poll = select.poll()
    poll.register(fd, select.POLLIN | select.POLLOUT)

    assert poll.poll() == [(fd, select.POLLIN)]
    assert time.time() == 2
```

## List of currently patched modules and functions

- time.time
- time.sleep
- datetime.datetime.today # Must import the module
- datetime.datetime.now
- datetime.datetime.utcnow
- select.select
- select.poll

### Add your own patches to time-travel

time-travel uses python "entry points" to add external patches to it.

#### Example
my_new_patcher.py:
```python
from time_travel.patchers.basic_patcher import BasicPatcher

class MyNewPatcher(BasicPatcher):
    def __init__(self, *args, **kwargs):
        pass
```

To add the new patcher automatically to time-travel, only add the new class to the "time_travel.patchers" entry point in your setup.py:
```python
from setuptools import setup

setup(
    name=...
    .
    .
    .
    entry_points={
        'time_travel.patchers' : [
            'my_new_patcher = my_new_patcher:MyNewPatcher',
        ],
    }
)
```


