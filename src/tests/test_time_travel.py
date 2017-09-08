from time_travel import TimeTravel

import time
import datetime as dtl
from datetime import datetime
import select
import mock


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
        import pdb
        pdb.set_trace()
        assert datetime.today() == datetime.fromtimestamp(0)
        
        time.sleep(3600)
        assert datetime.now() == datetime.fromtimestamp(3600)


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
