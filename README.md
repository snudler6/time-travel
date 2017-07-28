[![Build Status](https://travis-ci.org/snudler6/time-travel.svg?branch=master)](https://travis-ci.org/snudler6/time-travel)

# time-travel
python time libraries mocking

### time-travel is the fun and easy way to unit-test time sensetive modules.
### Can write determenistic test for long and even infinite time scenarios.

## Usage

`TimeTravel` is context manager patching all time modules currently patched
in a single line.

### Examples

#### Skip timouts

Tests are determenistic and take no time with time travel.

```python
with TimeTravel():  
    assert time.time() == 0
    time.sleep(3600)
    assert time.time() == 3600    
```

```python
with TimeTravel():
    assert datetime.today() == datetime.fromtimestamp(0)
    time.sleep(3600)
    assert datetime.today() == datetime.fromtimestamp(3600)
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


## List of currently patched modules and functions

- time.time
- time.time
- datetime.datetime.today
- select.select