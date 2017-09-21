from time_travel import TimeTravel

import time
from datetime import datetime
import select
import mock
import pytest
import sys
from datetime import datetime as datetime_cls


def test_time_patch_set_time():
    with TimeTravel(modules_to_patch=__name__) as t:
        
        assert time.time() == 100000
        t.clock.time += 360
        assert time.time() == 100360


def test_sleep_patch_sleep():
    with TimeTravel(modules_to_patch=(__name__,)) as t:
        
        assert time.time() == 100000
        time.sleep(3600)
        assert time.time() == 103600
        
        t.clock.time = 107200
        assert time.time() == 107200
        
        
def test_datetime_patch_set_time():
    with TimeTravel(modules_to_patch=[__name__]) as t:
        
        assert datetime_cls.today() == datetime_cls.fromtimestamp(100000)
        t.clock.time = 86400
        assert datetime_cls.today() == datetime_cls.fromtimestamp(86400)


def test_patch_without_module_name():
    with TimeTravel() as t:
        
        assert datetime_cls.utcnow() == datetime_cls.fromtimestamp(100000)
        t.clock.time = 103600
        assert datetime_cls.now() == datetime_cls.fromtimestamp(103600)


def test_patch_stop_afer_scope_end():
    with TimeTravel(modules_to_patch=__name__) as t:
        
        assert datetime_cls.now() == datetime_cls.fromtimestamp(100000)
        t.clock.time = 86400
        assert datetime_cls.today() == datetime_cls.fromtimestamp(86400)
            
    assert time.time() != 86400
    assert datetime_cls.today() != datetime_cls.fromtimestamp(100000)


def test_inner_importing_of_datetime():
    with TimeTravel(modules_to_patch=__name__):
        import datetime
        assert datetime.date.today() == datetime.date.fromtimestamp(100000)


def test_no_renaming_patching():
    with TimeTravel(modules_to_patch=__name__) as t:
        
        assert datetime.today() == datetime_cls.fromtimestamp(100000)
        t.clock.time = 200000
        assert datetime.today() == datetime_cls.fromtimestamp(200000)


def test_sleep_changing_datetime_now():
    with TimeTravel(modules_to_patch=__name__):
        assert datetime_cls.today() == datetime_cls.fromtimestamp(100000)
        time.sleep(3600)
        assert datetime_cls.now() == datetime_cls.fromtimestamp(103600)


def test_select_no_timeout():
    with TimeTravel(modules_to_patch=__name__) as t:
        event = mock.MagicMock()
        
        t.events_pool.add_future_event(100002,
                                       event,
                                       t.events_types.select.WRITE)
        
        assert select.select([], [event], []) == ([], [event], [])
        assert time.time() == 100002
        assert datetime_cls.today() == datetime_cls.fromtimestamp(100002)
      
        
def test_select_with_timeout():
    with TimeTravel(modules_to_patch=__name__) as t:
        event = mock.MagicMock()
        
        t.events_pool.add_future_event(100002,
                                       event,
                                       t.events_types.select.EXCEPTIONAL)
        
        assert select.select([], [], [event], 6) == ([], [], [event])
        assert time.time() == 100002
        assert datetime_cls.today() == datetime_cls.fromtimestamp(100002)
     
        
def test_select_timeout_occurring():
    with TimeTravel(modules_to_patch=__name__) as t:
        event = mock.MagicMock()
        
        t.events_pool.add_future_event(100010,
                                       event,
                                       t.events_types.select.READ)
        
        assert select.select([event], [], [], 6) == ([], [], [])
        assert time.time() == 100006
        assert datetime_cls.today() == datetime_cls.fromtimestamp(100006)


@pytest.mark.skipif(sys.platform == 'win32',
                    reason='select.poll is not supported under win32')
def test_poll():
    with TimeTravel(modules_to_patch=__name__) as t:
        fd = mock.MagicMock()
        t.events_pool.add_future_event(100002, fd, select.POLLIN)

        poll = select.poll()
        poll.register(fd, select.POLLIN | select.POLLOUT)

        assert poll.poll() == [(fd, select.POLLIN)]
        assert time.time() == 100002
