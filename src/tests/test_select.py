from time_travel.patchers.select_patcher import SelectPatcher
from time_travel.time_machine_clock import TimeMachineClock
from time_travel.events_pool import EventsPool
from .utils import _t

import select
import mock
import pytest


class TestSelectPatcher(object):

    def setup_method(self, method):
        """Start a select patcher"""
        self.events_pool = EventsPool()

        self.clock = TimeMachineClock(clock_listeners=[self.events_pool])
        
        self.patcher = SelectPatcher(self.clock, self.events_pool,
                                     modules_to_patch=__name__)
        
        self.patcher.start()
    
    def teardown_method(self, method):
        """Stop the select patcher"""
        self.patcher.stop()
        
    def test_basic_usage(self):
        fd = mock.MagicMock()
        self.events_pool.add_future_event(_t(2),
                                          fd,
                                          SelectPatcher.EventTypes.READ)
        
        assert select.select([fd], [], [], 17) == ([fd], [], [])
        assert self.clock.time == _t(2)

    def test_empty_lists(self):
        assert select.select([], [], [], 17) == ([], [], [])
        assert self.clock.time == _t(17)
    
    def test_future_event_after_timeout(self):
        fd = mock.MagicMock()
        self.events_pool.add_future_event(_t(27),
                                          fd,
                                          SelectPatcher.EventTypes.READ)
        
        assert select.select([], [fd], [], 17) == ([], [], [])
        assert self.clock.time == _t(17)
        
    def test_adding_unwaited_fds(self):
        first_fd = mock.MagicMock(name='first_fd')
        second_fd = mock.MagicMock(name='second_fd')
        waited_for_fd = mock.MagicMock(name='waited_for_fd')
        
        self.events_pool.add_future_event(_t(3),
                                          first_fd,
                                          SelectPatcher.EventTypes.READ)
        self.events_pool.add_future_event(_t(4),
                                          second_fd,
                                          SelectPatcher.EventTypes.WRITE)
        self.events_pool.add_future_event(_t(5),
                                          waited_for_fd,
                                          SelectPatcher.EventTypes.READ)
        
        assert select.select([waited_for_fd], [], [], 7) == \
            ([waited_for_fd], [], [])
        
        assert self.clock.time == _t(5)
        
    def test_multiple_fds_for_same_time(self):
        fd1 = mock.MagicMock(name='fd1')
        fd2 = mock.MagicMock(name='fd2')
        fd3 = mock.MagicMock(name='fd3')
        fd4 = mock.MagicMock(name='fd4')
        unwaited_fd = mock.MagicMock(name='unwaited_fd')
        
        self.events_pool.add_future_event(_t(3),
                                          fd1,
                                          SelectPatcher.EventTypes.READ)
        self.events_pool.add_future_event(_t(3),
                                          fd2,
                                          SelectPatcher.EventTypes.READ)
        self.events_pool.add_future_event(_t(3),
                                          fd3,
                                          SelectPatcher.EventTypes.WRITE)
        self.events_pool.add_future_event(_t(3),
                                          fd4,
                                          SelectPatcher.EventTypes.EXCEPTIONAL)
        self.events_pool.add_future_event(_t(3),
                                          unwaited_fd,
                                          SelectPatcher.EventTypes.READ)
        
        returned_events = select.select(
            [fd1, fd2],
            [fd3],
            [fd4],
            7
        )
        
        expected_events = ([fd1, fd2], [fd3], [fd4])
        
        for returned, expected in zip(returned_events, expected_events):
            assert set(returned) == set(expected)
        
        assert self.clock.time == _t(3)

    def test_fd_not_returned_twice(self):
        fd = mock.MagicMock()
        
        self.events_pool.add_future_event(_t(3),
                                          fd,
                                          SelectPatcher.EventTypes.EXCEPTIONAL)
        
        assert select.select([], [], [fd], 6) == ([], [], [fd])
        assert self.clock.time == _t(3)
        
        assert select.select([], [], [fd], 6) == ([], [], [])
        assert self.clock.time == _t(3 + 6)
          
    def test_same_fd_multiple_timestamps(self):
        fd = mock.MagicMock()
        
        self.events_pool.add_future_event(_t(1),
                                          fd,
                                          SelectPatcher.EventTypes.EXCEPTIONAL)
        self.events_pool.add_future_event(_t(2),
                                          fd,
                                          SelectPatcher.EventTypes.READ)
        self.events_pool.add_future_event(_t(2),
                                          fd,
                                          SelectPatcher.EventTypes.EXCEPTIONAL)
        
        assert select.select([], [], [fd], 6) == ([], [], [fd])
        assert self.clock.time == _t(1)
        
        assert select.select([fd], [], [fd], 6) == ([fd], [], [fd])
        assert self.clock.time == _t(2)

    def test_select_with_no_timeout(self):
        fd = mock.MagicMock()
        
        self.events_pool.add_future_event(_t(3),
                                          fd,
                                          SelectPatcher.EventTypes.READ)
        
        assert select.select([fd], [], []) == ([fd], [], [])
        assert self.clock.time == _t(3)

    def test_select_infinite_wait(self):
        fd = mock.MagicMock()
        
        with pytest.raises(ValueError):
            select.select([fd], [], [])
            
    def test_fd_returned_in_multiple_lists(self):
        fd = mock.MagicMock()
        
        self.events_pool.add_future_event(_t(1),
                                          fd,
                                          SelectPatcher.EventTypes.READ)
        self.events_pool.add_future_event(_t(1),
                                          fd,
                                          SelectPatcher.EventTypes.WRITE)
        self.events_pool.add_future_event(_t(1),
                                          fd,
                                          SelectPatcher.EventTypes.EXCEPTIONAL)
        
        assert select.select([fd], [fd], [fd], 6) == ([fd], [fd], [fd])
        assert self.clock.time == _t(1)
