from time_travel import TimeTravel

import time
from datetime import datetime
import select
import mock
import pytest
import sys


def test_time_patch_set_time():
    with TimeTravel() as t:
        
        assert time.time() == 0
        t.clock.time = 3600
        assert time.time() == 3600


def test_sleep_patch_sleep():
    with TimeTravel() as t:
        
        assert time.time() == 0
        time.sleep(3600)
        assert time.time() == 3600
        
        t.clock.time = 7200
        assert time.time() == 7200
        
        
def test_datetime_patch_set_time():
    with TimeTravel() as t:
        
        assert datetime.today() == datetime.fromtimestamp(0)
        t.clock.time = 3600
        assert datetime.today() == datetime.fromtimestamp(3600)
        

def test_sleep_changing_today():
    with TimeTravel():
        assert datetime.today() == datetime.fromtimestamp(0)
        
        time.sleep(3600)
        assert datetime.today() == datetime.fromtimestamp(3600)


def test_select_no_timeout():
    with TimeTravel() as t:
        event = mock.MagicMock()
        
        t.events_pool.add_future_event(2, event, t.events_types.select.WRITE)
        
        assert select.select([], [event], []) == ([], [event], [])
        assert time.time() == 2
        assert datetime.today() == datetime.fromtimestamp(2)
      
        
def test_select_with_timeout():
    with TimeTravel() as t:
        event = mock.MagicMock()
        
        t.events_pool.add_future_event(2,
                                       event,
                                       t.events_types.select.EXCEPTIONAL)
        
        assert select.select([], [], [event], 6) == ([], [], [event])
        assert time.time() == 2
        assert datetime.today() == datetime.fromtimestamp(2)
     
        
def test_select_timeout_occurring():
    with TimeTravel() as t:
        event = mock.MagicMock()
        
        t.events_pool.add_future_event(10, event, t.events_types.select.READ)
        
        assert select.select([event], [], [], 6) == ([], [], [])
        assert time.time() == 6
        assert datetime.today() == datetime.fromtimestamp(6)


@pytest.mark.skipif(sys.platform == 'win32',
                    reason='select.poll is not supported under win32')
def test_poll():
    with TimeTravel() as t:
        fd = mock.MagicMock()
        t.events_pool.add_future_event(2, fd, select.POLLIN)

        poll = select.poll()
        poll.register(fd, select.POLLIN | select.POLLOUT)

        assert poll.poll() == [(fd, select.POLLIN)]
        assert time.time() == 2
