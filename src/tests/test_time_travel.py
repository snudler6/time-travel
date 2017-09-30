from time_travel import TimeTravel
from .utils import _t

import time
import select
import mock
import pytest
import sys
from datetime import datetime
from datetime import datetime as datetime_cls


def test_time_patch_set_time():
    with TimeTravel(modules_to_patch=__name__) as t:
        
        assert time.time() == _t(0)
        t.clock.time += 360
        assert time.time() == _t(360)


def test_sleep_patch_sleep():
    with TimeTravel(modules_to_patch=(__name__,)) as t:

        assert time.time() == _t(0)
        time.sleep(200)
        assert time.time() == _t(200)

        t.clock.time = _t(6000)
        assert time.time() == _t(6000)
        
        
def test_datetime_patch_set_time():
    with TimeTravel(modules_to_patch=[__name__]) as t:
        
        assert datetime_cls.today() == datetime_cls.fromtimestamp(_t(0))
        t.clock.time = _t(1000)
        assert datetime_cls.today() == datetime_cls.fromtimestamp(_t(1000))


def test_patch_without_module_name():
    with TimeTravel() as t:
        
        assert datetime_cls.utcnow() == datetime_cls.fromtimestamp(_t(0))
        t.clock.time = _t(1000)
        assert datetime_cls.now() == datetime_cls.fromtimestamp(_t(1000))


def test_patch_stop_afer_scope_end():
    with TimeTravel(modules_to_patch=__name__) as t:
        
        assert datetime_cls.now() == datetime_cls.fromtimestamp(_t(0))
        t.clock.time = _t(1000)
        assert datetime_cls.today() == datetime_cls.fromtimestamp(_t(1000))
            
    assert time.time() != _t(1000)
    assert datetime_cls.today() != datetime_cls.fromtimestamp(_t(1000))


def test_inner_importing_of_datetime():
    with TimeTravel(modules_to_patch=__name__):
        import datetime
        assert datetime.date.today() == datetime.date.fromtimestamp(_t(0))


def test_no_renaming_patching():
    with TimeTravel(modules_to_patch=__name__) as t:
        
        assert datetime.today() == datetime_cls.fromtimestamp(_t(0))
        t.clock.time = _t(1000)
        assert datetime.today() == datetime_cls.fromtimestamp(_t(1000))


def test_sleep_changing_datetime_now():
    with TimeTravel(modules_to_patch=__name__):
        assert datetime_cls.today() == datetime_cls.fromtimestamp(_t(0))
        time.sleep(150)
        assert datetime_cls.now() == datetime_cls.fromtimestamp(_t(150))


def test_select_no_timeout():
    with TimeTravel(modules_to_patch=__name__) as t:
        fd = mock.MagicMock()
        
        t.add_future_event(2, fd, t.events_types.select.WRITE)

        now = t.clock.time
        assert select.select([], [fd], []) == ([], [fd], [])
        assert time.time() == now + 2
        assert datetime_cls.today() == datetime_cls.fromtimestamp(now + 2)
      
        
def test_select_with_timeout():
    with TimeTravel(modules_to_patch=__name__) as t:
        fd = mock.MagicMock()
        
        t.add_future_event(2, fd, t.events_types.select.EXCEPTIONAL)

        now = t.clock.time
        assert select.select([], [], [fd], 6) == ([], [], [fd])
        assert time.time() == now + 2
        assert datetime_cls.today() == datetime_cls.fromtimestamp(now + 2)
     
        
def test_select_timeout_occurring():
    with TimeTravel(modules_to_patch=__name__) as t:
        fd = mock.MagicMock()
        
        t.add_future_event(10, fd, t.events_types.select.READ)

        now = t.clock.time
        assert select.select([fd], [], [], 6) == ([], [], [])
        assert time.time() == now + 6
        assert datetime_cls.today() == datetime_cls.fromtimestamp(now + 6)


@pytest.mark.skipif(sys.platform == 'win32',
                    reason='select.poll is not supported under win32')
def test_poll():
    with TimeTravel(modules_to_patch=__name__) as t:
        fd = mock.MagicMock()
        t.add_future_event(2, fd, select.POLLIN)

        poll = select.poll()
        poll.register(fd, select.POLLIN | select.POLLOUT)

        now = t.clock.time
        assert poll.poll() == [(fd, select.POLLIN)]
        assert time.time() == now + 2
