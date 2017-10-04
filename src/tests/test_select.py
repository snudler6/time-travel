from time_travel.patchers.select_patcher import SelectPatcher
from time_travel.time_machine_clock import TimeMachineClock
from time_travel.event_pool import EventPool
from .utils import _t

import select
import socket
import pytest


class TestSelectPatcher(object):

    def setup_method(self, method):
        """Start a select patcher"""
        self.event_pool = EventPool()

        self.clock = TimeMachineClock(clock_listeners=[self.event_pool])
        
        self.patcher = SelectPatcher(self.clock,
                                     self.event_pool,
                                     modules_to_patch=__name__)
        self.patcher.start()
    
    def teardown_method(self, method):
        """Stop the select patcher"""
        self.patcher.stop()
        
    def test_basic_usage(self):
        sock = socket.socket()
        self.event_pool.add_future_event(_t(2),
                                         sock,
                                         SelectPatcher.EventTypes.READ)
        
        assert select.select([sock], [], [], 17) == ([sock], [], [])
        assert self.clock.time == _t(2)

    def test_empty_lists(self):
        assert select.select([], [], [], 17) == ([], [], [])
        assert self.clock.time == _t(17)
    
    def test_future_event_after_timeout(self):
        sock = socket.socket()
        self.event_pool.add_future_event(_t(27),
                                         sock,
                                         SelectPatcher.EventTypes.READ)
        
        assert select.select([], [sock], [], 17) == ([], [], [])
        assert self.clock.time == _t(17)
        
    def test_adding_unwaited_sockets(self):
        first_sock = socket.socket()
        second_sock = socket.socket()
        waited_for_sock = socket.socket()
        
        self.event_pool.add_future_event(_t(3),
                                         first_sock,
                                         SelectPatcher.EventTypes.READ)
        self.event_pool.add_future_event(_t(4),
                                         second_sock,
                                         SelectPatcher.EventTypes.WRITE)
        self.event_pool.add_future_event(_t(5),
                                         waited_for_sock,
                                         SelectPatcher.EventTypes.READ)
        
        assert select.select([waited_for_sock], [], [], 7) == \
            ([waited_for_sock], [], [])
        
        assert self.clock.time == _t(5)
        
    def test_multiple_sockets_for_same_time(self):
        sock1 = socket.socket()
        sock2 = socket.socket()
        sock3 = socket.socket()
        sock4 = socket.socket()
        unwaited_sock = socket.socket()
        
        self.event_pool.add_future_event(_t(3),
                                         sock1,
                                         SelectPatcher.EventTypes.READ)
        self.event_pool.add_future_event(_t(3),
                                         sock2,
                                         SelectPatcher.EventTypes.READ)
        self.event_pool.add_future_event(_t(3),
                                         sock3,
                                         SelectPatcher.EventTypes.WRITE)
        self.event_pool.add_future_event(_t(3),
                                         sock4,
                                         SelectPatcher.EventTypes.EXCEPTIONAL)
        self.event_pool.add_future_event(_t(3),
                                         unwaited_sock,
                                         SelectPatcher.EventTypes.READ)
        
        returned_events = select.select(
            [sock1, sock2],
            [sock3],
            [sock4],
            7
        )
        
        expected_events = ([sock1, sock2], [sock3], [sock4])
        
        for returned, expected in zip(returned_events, expected_events):
            assert set(returned) == set(expected)
        
        assert self.clock.time == _t(3)

    def test_socket_not_returned_twice(self):
        sock = socket.socket()
        
        self.event_pool.add_future_event(_t(3),
                                         sock,
                                         SelectPatcher.EventTypes.EXCEPTIONAL)
        
        assert select.select([], [], [sock], 6) == ([], [], [sock])
        assert self.clock.time == _t(3)
        
        assert select.select([], [], [sock], 6) == ([], [], [])
        assert self.clock.time == _t(3 + 6)
          
    def test_same_socket_multiple_timestamps(self):
        sock = socket.socket()
        
        self.event_pool.add_future_event(_t(1),
                                         sock,
                                         SelectPatcher.EventTypes.EXCEPTIONAL)
        self.event_pool.add_future_event(_t(2),
                                         sock,
                                         SelectPatcher.EventTypes.READ)
        self.event_pool.add_future_event(_t(2),
                                         sock,
                                         SelectPatcher.EventTypes.EXCEPTIONAL)
        
        assert select.select([], [], [sock], 6) == ([], [], [sock])
        assert self.clock.time == _t(1)
        
        assert select.select([sock], [], [sock], 6) == ([sock], [], [sock])
        assert self.clock.time == _t(2)

    def test_select_with_no_timeout(self):
        sock = socket.socket()
        
        self.event_pool.add_future_event(_t(3),
                                         sock,
                                         SelectPatcher.EventTypes.READ)
        
        assert select.select([sock], [], []) == ([sock], [], [])
        assert self.clock.time == _t(3)

    def test_select_infinite_wait(self):
        sock = socket.socket()
        
        with pytest.raises(ValueError):
            select.select([sock], [], [])
            
    def test_socket_returned_in_multiple_lists(self):
        sock = socket.socket()
        
        self.event_pool.add_future_event(_t(1),
                                         sock,
                                         SelectPatcher.EventTypes.READ)
        self.event_pool.add_future_event(_t(1),
                                         sock,
                                         SelectPatcher.EventTypes.WRITE)
        self.event_pool.add_future_event(_t(1),
                                         sock,
                                         SelectPatcher.EventTypes.EXCEPTIONAL)
        
        assert select.select([sock], [sock], [sock], 6) == \
            ([sock], [sock], [sock])
        assert self.clock.time == _t(1)
