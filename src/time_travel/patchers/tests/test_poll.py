from time_travel.patchers.poll_patcher import PollPatcher
from time_travel.time_machine_clock import TimeMachineClock
from time_travel.events_pool import EventsPool

import select
import mock
import sys
import pytest


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
        self.patcher = PollPatcher(self.clock, self.events_pool)
        self.patcher.start()

        self.poll = select.poll()
    
    def teardown_method(self, method):
        """Stop the poll patcher"""
        self.patcher.stop()
        
    def test_empty_with_timeout(self):
        assert self.poll.poll(sec2msec(11)) == []
        assert self.clock.time == 100011

    def test_empty_without_timeout(self):
        with pytest.raises(ValueError):
            self.poll.poll()

    def test_one_fd(self):
        fd = mock.MagicMock()
        self.events_pool.add_future_event(100002, fd, select.POLLIN)

        self.poll.register(fd, select.POLLIN)

        assert self.poll.poll(sec2msec(10)) == [(fd, select.POLLIN)]
        assert self.clock.time == 100002

    def test_timeout_before_event(self):
        fd = mock.MagicMock()
        self.events_pool.add_future_event(100010, fd, select.POLLIN)

        self.poll.register(fd, select.POLLIN)

        assert self.poll.poll(sec2msec(5)) == []
        assert self.clock.time == 100005
        
    def test_unregistered_events(self):
        first_fd = mock.MagicMock(name='first_fd')
        second_fd = mock.MagicMock(name='second_fd')
        expected_fd = mock.MagicMock(name='expected_fd')
        
        self.events_pool.add_future_event(100003, first_fd, select.POLLIN)
        self.events_pool.add_future_event(100004, second_fd, select.POLLIN)
        self.events_pool.add_future_event(100005, expected_fd, select.POLLIN)

        self.poll.register(expected_fd, select.POLLIN)
        
        assert self.poll.poll() == [(expected_fd, select.POLLIN)]
        assert self.clock.time == 100005
        
    def test_multiple_fds_same_time(self):
        fd1 = mock.MagicMock(name='fd1')
        fd2 = mock.MagicMock(name='fd2')
        fd3 = mock.MagicMock(name='fd3')
        far_fd = mock.MagicMock(name='far_fd')
        unwaited_fd = mock.MagicMock(name='unwaited_fd')
        
        self.events_pool.add_future_event(100003, fd1, select.POLLIN)
        self.events_pool.add_future_event(100003, fd2, select.POLLIN)
        self.events_pool.add_future_event(100003, fd3, select.POLLIN)
        self.events_pool.add_future_event(100005, far_fd, select.POLLIN)
        self.events_pool.add_future_event(100002, unwaited_fd, select.POLLIN)

        self.poll.register(fd1, select.POLLIN)
        self.poll.register(fd2, select.POLLIN)
        self.poll.register(fd3, select.POLLIN)
        self.poll.register(far_fd, select.POLLIN)

        assert set(self.poll.poll()) == set([(fd1, select.POLLIN),
                                             (fd2, select.POLLIN),
                                             (fd3, select.POLLIN)])
        assert self.clock.time == 100003

    def test_same_fd_multiple_events(self):
        fd = mock.MagicMock()

        self.events_pool.add_future_event(100003, fd, select.POLLIN)
        self.events_pool.add_future_event(100003, fd, select.POLLOUT)
        self.events_pool.add_future_event(100005, fd, select.POLLHUP)

        self.poll.register(fd, select.POLLIN | select.POLLOUT | select.POLLHUP)

        assert self.poll.poll() == [(fd, select.POLLIN | select.POLLOUT)]
        assert self.clock.time == 100003

    def test_event_not_in_mask(self):
        fd = mock.MagicMock()

        self.events_pool.add_future_event(100003, fd, select.POLLIN)

        self.poll.register(fd, select.POLLOUT)

        assert self.poll.poll(sec2msec(25)) == []
        assert self.clock.time == 100025

    def test_event_not_returned_twice(self):
        fd = mock.MagicMock()
        
        self.events_pool.add_future_event(100003, fd, select.POLLIN)
        self.poll.register(fd, select.POLLIN)

        assert self.poll.poll(sec2msec(5)) == [(fd, select.POLLIN)]
        assert self.clock.time == 100003

        assert self.poll.poll(sec2msec(5)) == []
        assert self.clock.time == 100003 + 5
          
    def test_same_event_multiple_timestamps(self):
        fd = mock.MagicMock()
        
        self.events_pool.add_future_event(100001, fd, select.POLLIN)
        self.events_pool.add_future_event(100002, fd, select.POLLIN)
        self.events_pool.add_future_event(100002, fd, select.POLLOUT)

        self.poll.register(fd, select.POLLIN | select.POLLOUT)

        assert self.poll.poll() == [(fd, select.POLLIN)]
        assert self.clock.time == 100001

        assert self.poll.poll() == [(fd, select.POLLIN | select.POLLOUT)]
        assert self.clock.time == 100002

    def test_unregister(self):
        fd = mock.MagicMock()

        self.events_pool.add_future_event(100001, fd, select.POLLIN)
        self.events_pool.add_future_event(100005, fd, select.POLLIN)

        self.poll.register(fd, select.POLLIN)

        assert self.poll.poll() == [(fd, select.POLLIN)]
        assert self.clock.time == 100001

        self.poll.unregister(fd)

        assert self.poll.poll(sec2msec(10)) == []
        assert self.clock.time == 100001 + 10

    def test_modify(self):
        fd = mock.MagicMock()

        self.events_pool.add_future_event(100001, fd, select.POLLIN)
        self.events_pool.add_future_event(100005, fd, select.POLLIN)
        self.events_pool.add_future_event(100010, fd, select.POLLOUT)

        self.poll.register(fd, select.POLLIN)

        assert self.poll.poll() == [(fd, select.POLLIN)]
        assert self.clock.time == 100001

        self.poll.modify(fd, select.POLLOUT)

        assert self.poll.poll() == [(fd, select.POLLOUT)]
        assert self.clock.time == 100010
