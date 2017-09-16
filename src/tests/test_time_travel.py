from time_travel import TimeTravel

import time
from datetime import datetime
import select
import mock
from datetime import datetime as datetime_cls


def test_time_patch_set_time():
    with TimeTravel(name=__name__) as t:
        
        assert time.time() == 0
        t.clock.time = 3600
        assert time.time() == 3600


def test_sleep_patch_sleep():
    with TimeTravel(name=__name__) as t:
        
        assert time.time() == 0
        time.sleep(3600)
        assert time.time() == 3600
        
        t.clock.time = 7200
        assert time.time() == 7200
        
        
def test_datetime_patch_set_time():
    with TimeTravel(name=__name__) as t:
        
        assert datetime_cls.today() == datetime_cls.fromtimestamp(0)
        t.clock.time = 3600
        assert datetime_cls.today() ==\
            datetime_cls.fromtimestamp(3600)
            
            
def test_sub_module_patching():
    with TimeTravel(name=__name__) as t:
        
        assert datetime_cls.today() == datetime_cls.fromtimestamp(0)
        t.clock.time = 3600
        assert datetime_cls.today() == datetime_cls.fromtimestamp(3600)
                

def test_sleep_changing_datetime_now():
    with TimeTravel(name=__name__):
        assert datetime_cls.today() == datetime_cls.fromtimestamp(0)
        time.sleep(3600)
        assert datetime_cls.now() == datetime_cls.fromtimestamp(3600)


def test_select_no_timeout():
    with TimeTravel(name=__name__) as t:
        event = mock.MagicMock()
        
        t.events_pool.add_future_event(2, event, t.events_types.select.WRITE)
        
        assert select.select([], [event], []) == ([], [event], [])
        assert time.time() == 2
        assert datetime_cls.today() == datetime_cls.fromtimestamp(2)
      
        
def test_select_with_timeout():
    with TimeTravel(name=__name__) as t:
        event = mock.MagicMock()
        
        t.events_pool.add_future_event(2,
                                       event,
                                       t.events_types.select.EXCEPTIONAL)
        
        assert select.select([], [], [event], 6) == ([], [], [event])
        assert time.time() == 2
        assert datetime_cls.today() == datetime_cls.fromtimestamp(2)
     
        
def test_select_timeout_occurring():
    with TimeTravel(name=__name__) as t:
        event = mock.MagicMock()
        
        t.events_pool.add_future_event(10, event, t.events_types.select.READ)
        
        assert select.select([event], [], [], 6) == ([], [], [])
        assert time.time() == 6
        assert datetime_cls.today() == datetime_cls.fromtimestamp(6)
