from time_travel.patchers.poll_patcher import PollPatcher
from time_travel.time_machine_clock import TimeMachineClock
from time_travel.events_pool import EventsPool

import select
import mock
import pytest


def sec2msec(sec):
    """Convert `sec` to milliseconds."""
    return int(sec * 1000)


class TestPollPatcher(object):

    def setup_method(self, method):
        """Start a poll patcher"""
        self.events_pool = EventsPool()
        self.clock = TimeMachineClock(clock_listeners=[self.events_pool])
        self.patcher = PollPatcher(self.clock, self.events_pool)
        self.patcher.start()

        self.poll = select.poll()
    
    def teardown_method(self, method):
        """Stop the poll patcher"""
        self.patcher.stop()
        
    def test_empty_with_timeout(self):
        assert self.poll.poll(sec2msec(11)) == []
        assert self.clock.time == 11

    def test_empty_without_timeout(self):
        with pytest.raises(ValueError):
            self.poll.poll()

    def test_one_event(self):
        event = mock.MagicMock()
        self.events_pool.add_future_event(2,
                                          event,
                                          select.POLLIN)

        self.poll.register(event, select.POLLIN)

        assert self.poll.poll(sec2msec(10)) == [(event, select.POLLIN)]
        assert self.clock.time == 2

    def test_timeout_before_event(self):
        event = mock.MagicMock()
        self.events_pool.add_future_event(10,
                                          event,
                                          select.POLLIN)

        self.poll.register(event, select.POLLIN)

        assert self.poll.poll(sec2msec(5)) == []
        assert self.clock.time == 5
        
    def test_unregistered_events(self):
        first_event = mock.MagicMock(name='first_event')
        second_event = mock.MagicMock(name='second_event')
        expected_event = mock.MagicMock(name='expected_event')
        
        self.events_pool.add_future_event(3,
                                          first_event,
                                          select.POLLIN)
        self.events_pool.add_future_event(4,
                                          second_event,
                                          select.POLLIN)
        self.events_pool.add_future_event(5,
                                          expected_event,
                                          select.POLLIN)

        self.poll.register(expected_event, select.POLLIN)
        
        assert self.poll.poll() == [(expected_event, select.POLLIN)]
        assert self.clock.time == 5
        
    def test_multiple_objects_same_time(self):
        event1 = mock.MagicMock(name='event1')
        event2 = mock.MagicMock(name='event2')
        event3 = mock.MagicMock(name='event3')
        far_event = mock.MagicMock(name='far_event')
        unwaited_event = mock.MagicMock(name='unwaited_event')
        
        self.events_pool.add_future_event(3, event1, select.POLLIN)
        self.events_pool.add_future_event(3, event2, select.POLLIN)
        self.events_pool.add_future_event(3, event3, select.POLLIN)
        self.events_pool.add_future_event(5, far_event, select.POLLIN)
        self.events_pool.add_future_event(2, unwaited_event, select.POLLIN)

        self.poll.register(event1, select.POLLIN)
        self.poll.register(event2, select.POLLIN)
        self.poll.register(event3, select.POLLIN)
        self.poll.register(far_event, select.POLLIN)

        assert set(self.poll.poll()) == set([(event1, select.POLLIN),
                                             (event2, select.POLLIN),
                                             (event3, select.POLLIN)])
        assert self.clock.time == 3

    def test_same_object_multiple_events(self):
        event = mock.MagicMock()

        self.events_pool.add_future_event(3, event, select.POLLIN)
        self.events_pool.add_future_event(3, event, select.POLLOUT)
        self.events_pool.add_future_event(5, event, select.POLLHUP)

        self.poll.register(event,
                           select.POLLIN | select.POLLOUT | select.POLLHUP)

        assert self.poll.poll() == [(event, select.POLLIN | select.POLLOUT)]
        assert self.clock.time == 3

    def test_event_not_in_mask(self):
        event = mock.MagicMock()

        self.events_pool.add_future_event(3, event, select.POLLIN)

        self.poll.register(event, select.POLLOUT)

        assert self.poll.poll(sec2msec(25)) == []
        assert self.clock.time == 25

    def test_event_not_returned_twice(self):
        event = mock.MagicMock()
        
        self.events_pool.add_future_event(3, event, select.POLLIN)
        self.poll.register(event, select.POLLIN)

        assert self.poll.poll(sec2msec(5)) == [(event, select.POLLIN)]
        assert self.clock.time == 3

        assert self.poll.poll(sec2msec(5)) == []
        assert self.clock.time == 3 + 5
          
    def test_same_event_multiple_timestamps(self):
        event = mock.MagicMock()
        
        self.events_pool.add_future_event(1, event, select.POLLIN)
        self.events_pool.add_future_event(2, event, select.POLLIN)
        self.events_pool.add_future_event(2, event, select.POLLOUT)

        self.poll.register(event, select.POLLIN | select.POLLOUT)

        assert self.poll.poll() == [(event, select.POLLIN)]
        assert self.clock.time == 1

        assert self.poll.poll() == [(event, select.POLLIN | select.POLLOUT)]
        assert self.clock.time == 2

    def test_unregister_event(self):
        event = mock.MagicMock()

        self.events_pool.add_future_event(1, event, select.POLLIN)
        self.events_pool.add_future_event(5, event, select.POLLIN)

        self.poll.register(event, select.POLLIN)

        assert self.poll.poll() == [(event, select.POLLIN)]
        assert self.clock.time == 1

        self.poll.unregister(event)

        assert self.poll.poll(sec2msec(10)) == []
        assert self.clock.time == 1 + 10

    def test_modify_event(self):
        event = mock.MagicMock()

        self.events_pool.add_future_event(1, event, select.POLLIN)
        self.events_pool.add_future_event(5, event, select.POLLIN)
        self.events_pool.add_future_event(10, event, select.POLLOUT)

        self.poll.register(event, select.POLLIN)

        assert self.poll.poll() == [(event, select.POLLIN)]
        assert self.clock.time == 1

        self.poll.modify(event, select.POLLOUT)

        assert self.poll.poll() == [(event, select.POLLOUT)]
        assert self.clock.time == 10
