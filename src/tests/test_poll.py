from time_travel.patchers.poll_patcher import PollPatcher
from time_travel.time_machine_clock import TimeMachineClock
from time_travel.event_pool import EventPool
from .utils import _t

import select
import socket
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

    def test_one_socket(self):
        sock = socket.socket()
        self.event_pool.add_future_event(_t(2), sock, select.POLLIN)

        self.poll.register(sock, select.POLLIN)

        assert self.poll.poll(sec2msec(10)) == [(sock, select.POLLIN)]
        assert self.clock.time == _t(2)

    def test_timeout_before_event(self):
        sock = socket.socket()
        self.event_pool.add_future_event(_t(10), sock, select.POLLIN)

        self.poll.register(sock, select.POLLIN)

        assert self.poll.poll(sec2msec(5)) == []
        assert self.clock.time == _t(5)

    def test_unregistered_events(self):
        first_sock = socket.socket()
        second_sock = socket.socket()
        expected_sock = socket.socket()

        self.event_pool.add_future_event(_t(3), first_sock, select.POLLIN)
        self.event_pool.add_future_event(_t(4), second_sock, select.POLLIN)
        self.event_pool.add_future_event(_t(5), expected_sock, select.POLLIN)

        self.poll.register(expected_sock, select.POLLIN)

        assert self.poll.poll() == [(expected_sock, select.POLLIN)]
        assert self.clock.time == _t(5)

    def test_multiple_sockets_same_time(self):
        sock1 = socket.socket()
        sock2 = socket.socket()
        sock3 = socket.socket()
        far_sock = socket.socket()
        unwaited_sock = socket.socket()

        self.event_pool.add_future_event(_t(3), sock1, select.POLLIN)
        self.event_pool.add_future_event(_t(3), sock2, select.POLLIN)
        self.event_pool.add_future_event(_t(3), sock3, select.POLLIN)
        self.event_pool.add_future_event(_t(5), far_sock, select.POLLIN)
        self.event_pool.add_future_event(_t(2), unwaited_sock, select.POLLIN)

        self.poll.register(sock1, select.POLLIN)
        self.poll.register(sock2, select.POLLIN)
        self.poll.register(sock3, select.POLLIN)
        self.poll.register(far_sock, select.POLLIN)

        assert set(self.poll.poll()) == set([(sock1, select.POLLIN),
                                             (sock2, select.POLLIN),
                                             (sock3, select.POLLIN)])
        assert self.clock.time == _t(3)

    def test_same_socket_multiple_events(self):
        sock = socket.socket()

        self.event_pool.add_future_event(_t(3), sock, select.POLLIN)
        self.event_pool.add_future_event(_t(3), sock, select.POLLOUT)
        self.event_pool.add_future_event(_t(5), sock, select.POLLHUP)

        self.poll.register(sock,
                           select.POLLIN | select.POLLOUT | select.POLLHUP)

        assert self.poll.poll() == [(sock, select.POLLIN | select.POLLOUT)]
        assert self.clock.time == _t(3)

    def test_event_not_in_mask(self):
        sock = socket.socket()

        self.event_pool.add_future_event(_t(3), sock, select.POLLIN)

        self.poll.register(sock, select.POLLOUT)

        assert self.poll.poll(sec2msec(25)) == []
        assert self.clock.time == _t(25)

    def test_event_not_returned_twice(self):
        sock = socket.socket()

        self.event_pool.add_future_event(_t(3), sock, select.POLLIN)
        self.poll.register(sock, select.POLLIN)

        assert self.poll.poll(sec2msec(5)) == [(sock, select.POLLIN)]
        assert self.clock.time == _t(3)

        assert self.poll.poll(sec2msec(5)) == []
        assert self.clock.time == _t(3 + 5)

    def test_same_event_multiple_timestamps(self):
        sock = socket.socket()

        self.event_pool.add_future_event(_t(1), sock, select.POLLIN)
        self.event_pool.add_future_event(_t(2), sock, select.POLLIN)
        self.event_pool.add_future_event(_t(2), sock, select.POLLOUT)

        self.poll.register(sock, select.POLLIN | select.POLLOUT)

        assert self.poll.poll() == [(sock, select.POLLIN)]
        assert self.clock.time == _t(1)

        assert self.poll.poll() == [(sock, select.POLLIN | select.POLLOUT)]
        assert self.clock.time == _t(2)

    def test_unregister(self):
        sock = socket.socket()

        self.event_pool.add_future_event(_t(1), sock, select.POLLIN)
        self.event_pool.add_future_event(_t(5), sock, select.POLLIN)

        self.poll.register(sock, select.POLLIN)

        assert self.poll.poll() == [(sock, select.POLLIN)]
        assert self.clock.time == _t(1)

        self.poll.unregister(sock)

        assert self.poll.poll(sec2msec(10)) == []
        assert self.clock.time == _t(1 + 10)

    def test_modify(self):
        sock = socket.socket()

        self.event_pool.add_future_event(_t(1), sock, select.POLLIN)
        self.event_pool.add_future_event(_t(5), sock, select.POLLIN)
        self.event_pool.add_future_event(_t(10), sock, select.POLLOUT)

        self.poll.register(sock, select.POLLIN)

        assert self.poll.poll() == [(sock, select.POLLIN)]
        assert self.clock.time == _t(1)

        self.poll.modify(sock, select.POLLOUT)

        assert self.poll.poll() == [(sock, select.POLLOUT)]
        assert self.clock.time == _t(10)
