from time_travel.patchers.select_patcher import SelectPatcher
from time_travel.time_machine_clock import TimeMachineClock
from time_travel.events_pool import EventsPool

import select
import mock
import pytest


class TestSelectPatcher(object):

    def setup_method(self, method):
        """Start a select patcher"""
        self.events_pool = EventsPool()

        self.clock = TimeMachineClock(clock_listeners=[self.events_pool])
        
        self.patcher = SelectPatcher(self.clock, self.events_pool)
        self.patcher.start()
    
    def teardown_method(self, method):
        """Stop the select patcher"""
        self.patcher.stop()

    def test_empty_lists(self):
        assert select.select([], [], [], 17) == []
        assert self.clock.timestamp == 17
    
    def test_future_event_after_timeout(self):
        event = mock.MagicMock()
        self.events_pool.add_future_event(27, event)
        
        assert select.select([], [event], [], 17) == []
        assert self.clock.timestamp == 17
        
    def test_adding_unwaited_events(self):
        first_event = mock.MagicMock(name='first_event')
        second_event = mock.MagicMock(name='second_event')
        waited_for_event = mock.MagicMock(name='waited_for_event')
        
        self.events_pool.add_future_event(3, first_event)
        self.events_pool.add_future_event(4, second_event)
        self.events_pool.add_future_event(5, waited_for_event)
        
        assert select.select([waited_for_event], [], [], 7) == \
            [waited_for_event]
        
        assert self.clock.timestamp== 5
        
    def test_multiple_events_for_same_time(self):
        event1 = mock.MagicMock(name='event1')
        event2 = mock.MagicMock(name='event2')
        event3 = mock.MagicMock(name='event3')
        event4 = mock.MagicMock(name='event4')
        unwaited_event = mock.MagicMock(name='unwaited_event')
        
        self.events_pool.add_future_event(3, event1)
        self.events_pool.add_future_event(3, event2)
        self.events_pool.add_future_event(3, event3)
        self.events_pool.add_future_event(3, event4)
        self.events_pool.add_future_event(3, unwaited_event)
        
        returned_events = set(select.select(
            [event1, event2],
            [event3],
            [event4],
            7
        ))
        
        expected_events = set([event1, event2, event3, event4])
        
        assert returned_events >= expected_events
        assert expected_events >= returned_events
        
        assert self.clock.timestamp == 3    

    def test_event_not_returned_twice(self):
        event = mock.MagicMock()
        
        self.events_pool.add_future_event(3, event)
        
        assert select.select([], [], [event], 6) == [event]
        assert self.clock.timestamp == 3
        
        assert select.select([], [], [event], 6) == []
        assert self.clock.timestamp == 3 + 6
          
    def test_same_event_multiple_timestamps(self):
        event = mock.MagicMock()
        
        self.events_pool.add_future_event(1, event)
        self.events_pool.add_future_event(2, event)
        
        assert select.select([], [], [event], 6) == [event]
        assert self.clock.timestamp == 1
        
        assert select.select([event], [], [event], 6) == [event]
        assert self.clock.timestamp == 2

    def test_select_with_no_timeout(self):
        event = mock.MagicMock()
        
        self.events_pool.add_future_event(3, event)
        
        assert select.select([event], [], []) == [event]
        assert self.clock.timestamp == 3

    def test_select_infinite_wait(self):
        event = mock.MagicMock()
        
        with pytest.raises(ValueError):
            select.select([event], [], [])
