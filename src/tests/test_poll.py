from time_travel.patchers.poll_patcher import PollPatcher
from time_travel.time_machine_clock import TimeMachineClock
from time_travel.event_pool import EventPool
from .utils import _t

import select
import pytest


def sec2msec(sec):
    """Convert `sec` to milliseconds."""
    return int(sec * 1000)


@pytest.mark.skipif(not hasattr(select, 'poll'),
                    reason='select.poll is not supported in this platform')
class TestPollPatcher(object):

    def setup_method(self, method):
        """Start a poll patcher"""
        self.event_pool = EventPool()
        self.clock = TimeMachineClock(clock_listeners=[self.event_pool])
        self.patcher = PollPatcher(self.clock,
                                   self.event_pool,
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
        fd = 1
        self.event_pool.add_future_event(_t(2), fd, select.POLLIN)

        self.poll.register(fd, select.POLLIN)

        assert self.poll.poll(sec2msec(10)) == [(fd, select.POLLIN)]
        assert self.clock.time == _t(2)

    def test_timeout_before_event(self):
        fd = 7
        self.event_pool.add_future_event(_t(10), fd, select.POLLIN)

        self.poll.register(fd, select.POLLIN)

        assert self.poll.poll(sec2msec(5)) == []
        assert self.clock.time == _t(5)
        
    def test_unregistered_events(self):
        first_fd = 1
        second_fd = 2
        expected_fd = 3
        
        self.event_pool.add_future_event(_t(3), first_fd, select.POLLIN)
        self.event_pool.add_future_event(_t(4), second_fd, select.POLLIN)
        self.event_pool.add_future_event(_t(5), expected_fd, select.POLLIN)

        self.poll.register(expected_fd, select.POLLIN)
        
        assert self.poll.poll() == [(expected_fd, select.POLLIN)]
        assert self.clock.time == _t(5)
        
    def test_multiple_fds_same_time(self):
        fd1 = 1
        fd2 = 2
        fd3 = 3
        far_fd = 4
        unwaited_fd = 5
        
        self.event_pool.add_future_event(_t(3), fd1, select.POLLIN)
        self.event_pool.add_future_event(_t(3), fd2, select.POLLIN)
        self.event_pool.add_future_event(_t(3), fd3, select.POLLIN)
        self.event_pool.add_future_event(_t(5), far_fd, select.POLLIN)
        self.event_pool.add_future_event(_t(2), unwaited_fd, select.POLLIN)

        self.poll.register(fd1, select.POLLIN)
        self.poll.register(fd2, select.POLLIN)
        self.poll.register(fd3, select.POLLIN)
        self.poll.register(far_fd, select.POLLIN)

        assert set(self.poll.poll()) == set([(fd1, select.POLLIN),
                                             (fd2, select.POLLIN),
                                             (fd3, select.POLLIN)])
        assert self.clock.time == _t(3)

    def test_same_fd_multiple_events(self):
        fd = 5

        self.event_pool.add_future_event(_t(3), fd, select.POLLIN)
        self.event_pool.add_future_event(_t(3), fd, select.POLLOUT)
        self.event_pool.add_future_event(_t(5), fd, select.POLLHUP)

        self.poll.register(fd, select.POLLIN | select.POLLOUT | select.POLLHUP)

        assert self.poll.poll() == [(fd, select.POLLIN | select.POLLOUT)]
        assert self.clock.time == _t(3)

    def test_event_not_in_mask(self):
        fd = 8

        self.event_pool.add_future_event(_t(3), fd, select.POLLIN)

        self.poll.register(fd, select.POLLOUT)

        assert self.poll.poll(sec2msec(25)) == []
        assert self.clock.time == _t(25)

    def test_event_not_returned_twice(self):
        fd = 2
        
        self.event_pool.add_future_event(_t(3), fd, select.POLLIN)
        self.poll.register(fd, select.POLLIN)

        assert self.poll.poll(sec2msec(5)) == [(fd, select.POLLIN)]
        assert self.clock.time == _t(3)

        assert self.poll.poll(sec2msec(5)) == []
        assert self.clock.time == _t(3 + 5)
          
    def test_same_event_multiple_timestamps(self):
        fd = 1
        
        self.event_pool.add_future_event(_t(1), fd, select.POLLIN)
        self.event_pool.add_future_event(_t(2), fd, select.POLLIN)
        self.event_pool.add_future_event(_t(2), fd, select.POLLOUT)

        self.poll.register(fd, select.POLLIN | select.POLLOUT)

        assert self.poll.poll() == [(fd, select.POLLIN)]
        assert self.clock.time == _t(1)

        assert self.poll.poll() == [(fd, select.POLLIN | select.POLLOUT)]
        assert self.clock.time == _t(2)

    def test_unregister(self):
        fd = 9

        self.event_pool.add_future_event(_t(1), fd, select.POLLIN)
        self.event_pool.add_future_event(_t(5), fd, select.POLLIN)

        self.poll.register(fd, select.POLLIN)

        assert self.poll.poll() == [(fd, select.POLLIN)]
        assert self.clock.time == _t(1)

        self.poll.unregister(fd)

        assert self.poll.poll(sec2msec(10)) == []
        assert self.clock.time == _t(1 + 10)

    def test_modify(self):
        fd = 5

        self.event_pool.add_future_event(_t(1), fd, select.POLLIN)
        self.event_pool.add_future_event(_t(5), fd, select.POLLIN)
        self.event_pool.add_future_event(_t(10), fd, select.POLLOUT)

        self.poll.register(fd, select.POLLIN)

        assert self.poll.poll() == [(fd, select.POLLIN)]
        assert self.clock.time == _t(1)

        self.poll.modify(fd, select.POLLOUT)

        assert self.poll.poll() == [(fd, select.POLLOUT)]
        assert self.clock.time == _t(10)
