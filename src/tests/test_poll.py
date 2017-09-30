from time_travel.patchers.poll_patcher import PollPatcher
from time_travel.time_machine_clock import TimeMachineClock
from time_travel.events_pool import EventsPool
from .utils import _t

import select
import pytest
import mock
import sys


def sec2msec(sec):
    """Convert `sec` to milliseconds."""
    return int(sec * 1000)


@pytest.mark.skipif(sys.platform == 'win32',
                    reason='select.poll is not supported under win32')
class TestPollPatcher(object):

    def setup_method(self, method):
        """Start a poll patcher"""
        self.events_pool = EventsPool()
        self.clock = TimeMachineClock(clock_listeners=[self.events_pool])
        self.patcher = PollPatcher(self.clock, self.events_pool,
                                   modules_to_patch=__name__)
        self.patcher.start()

        self.poll = select.poll()
    
    def teardown_method(self, method):
        """Stop the poll patcher"""
        self.patcher.stop()
        
    def test_empty_with_timeout(self):
        assert self.poll.poll(sec2msec(11)) == []
        assert self.clock.time == _t(11)

    def test_empty_without_timeout(self):
        with pytest.raises(ValueError):
            self.poll.poll()

    def test_one_fd(self):
        fd = mock.MagicMock()
        self.events_pool.add_future_event(_t(2), fd, select.POLLIN)

        self.poll.register(fd, select.POLLIN)

        assert self.poll.poll(sec2msec(10)) == [(fd, select.POLLIN)]
        assert self.clock.time == _t(2)

    def test_timeout_before_event(self):
        fd = mock.MagicMock()
        self.events_pool.add_future_event(_t(10), fd, select.POLLIN)

        self.poll.register(fd, select.POLLIN)

        assert self.poll.poll(sec2msec(5)) == []
        assert self.clock.time == _t(5)
        
    def test_unregistered_events(self):
        first_fd = mock.MagicMock(name='first_fd')
        second_fd = mock.MagicMock(name='second_fd')
        expected_fd = mock.MagicMock(name='expected_fd')
        
        self.events_pool.add_future_event(_t(3), first_fd, select.POLLIN)
        self.events_pool.add_future_event(_t(4), second_fd, select.POLLIN)
        self.events_pool.add_future_event(_t(5), expected_fd, select.POLLIN)

        self.poll.register(expected_fd, select.POLLIN)
        
        assert self.poll.poll() == [(expected_fd, select.POLLIN)]
        assert self.clock.time == _t(5)
        
    def test_multiple_fds_same_time(self):
        fd1 = mock.MagicMock(name='fd1')
        fd2 = mock.MagicMock(name='fd2')
        fd3 = mock.MagicMock(name='fd3')
        far_fd = mock.MagicMock(name='far_fd')
        unwaited_fd = mock.MagicMock(name='unwaited_fd')
        
        self.events_pool.add_future_event(_t(3), fd1, select.POLLIN)
        self.events_pool.add_future_event(_t(3), fd2, select.POLLIN)
        self.events_pool.add_future_event(_t(3), fd3, select.POLLIN)
        self.events_pool.add_future_event(_t(5), far_fd, select.POLLIN)
        self.events_pool.add_future_event(_t(2), unwaited_fd, select.POLLIN)

        self.poll.register(fd1, select.POLLIN)
        self.poll.register(fd2, select.POLLIN)
        self.poll.register(fd3, select.POLLIN)
        self.poll.register(far_fd, select.POLLIN)

        assert set(self.poll.poll()) == set([(fd1, select.POLLIN),
                                             (fd2, select.POLLIN),
                                             (fd3, select.POLLIN)])
        assert self.clock.time == _t(3)

    def test_same_fd_multiple_events(self):
        fd = mock.MagicMock()

        self.events_pool.add_future_event(_t(3), fd, select.POLLIN)
        self.events_pool.add_future_event(_t(3), fd, select.POLLOUT)
        self.events_pool.add_future_event(_t(5), fd, select.POLLHUP)

        self.poll.register(fd, select.POLLIN | select.POLLOUT | select.POLLHUP)

        assert self.poll.poll() == [(fd, select.POLLIN | select.POLLOUT)]
        assert self.clock.time == _t(3)

    def test_event_not_in_mask(self):
        fd = mock.MagicMock()

        self.events_pool.add_future_event(_t(3), fd, select.POLLIN)

        self.poll.register(fd, select.POLLOUT)

        assert self.poll.poll(sec2msec(25)) == []
        assert self.clock.time == _t(25)

    def test_event_not_returned_twice(self):
        fd = mock.MagicMock()
        
        self.events_pool.add_future_event(_t(3), fd, select.POLLIN)
        self.poll.register(fd, select.POLLIN)

        assert self.poll.poll(sec2msec(5)) == [(fd, select.POLLIN)]
        assert self.clock.time == _t(3)

        assert self.poll.poll(sec2msec(5)) == []
        assert self.clock.time == _t(3 + 5)
          
    def test_same_event_multiple_timestamps(self):
        fd = mock.MagicMock()
        
        self.events_pool.add_future_event(_t(1), fd, select.POLLIN)
        self.events_pool.add_future_event(_t(2), fd, select.POLLIN)
        self.events_pool.add_future_event(_t(2), fd, select.POLLOUT)

        self.poll.register(fd, select.POLLIN | select.POLLOUT)

        assert self.poll.poll() == [(fd, select.POLLIN)]
        assert self.clock.time == _t(1)

        assert self.poll.poll() == [(fd, select.POLLIN | select.POLLOUT)]
        assert self.clock.time == _t(2)

    def test_unregister(self):
        fd = mock.MagicMock()

        self.events_pool.add_future_event(_t(1), fd, select.POLLIN)
        self.events_pool.add_future_event(_t(5), fd, select.POLLIN)

        self.poll.register(fd, select.POLLIN)

        assert self.poll.poll() == [(fd, select.POLLIN)]
        assert self.clock.time == _t(1)

        self.poll.unregister(fd)

        assert self.poll.poll(sec2msec(10)) == []
        assert self.clock.time == _t(1 + 10)

    def test_modify(self):
        fd = mock.MagicMock()

        self.events_pool.add_future_event(_t(1), fd, select.POLLIN)
        self.events_pool.add_future_event(_t(5), fd, select.POLLIN)
        self.events_pool.add_future_event(_t(10), fd, select.POLLOUT)

        self.poll.register(fd, select.POLLIN)

        assert self.poll.poll() == [(fd, select.POLLIN)]
        assert self.clock.time == _t(1)

        self.poll.modify(fd, select.POLLOUT)

        assert self.poll.poll() == [(fd, select.POLLOUT)]
        assert self.clock.time == _t(10)
