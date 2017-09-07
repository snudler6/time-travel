"""A patch to the datetime module."""

from .basic_patcher import BasicPatcher

import select as select_lib
from enum import Enum
import mock


class SelectPatcher(BasicPatcher):
    """Patcher for select module.
    
    patching:
        - select.select
    """
    
    EVENTS_NAMESPACE = 'select'
    EventTypes = Enum('select', ['READ', 'WRITE', 'EXCEPTIONAL'])
    
    def __init__(self, *args, **kwargs):
        """Create the patch."""
        super(SelectPatcher, self).__init__(*args, **kwargs)
        
        self.select = mock.Mock(
            side_effect=self._mocked_select,
            spec=select_lib.select)
        
        self.patches = [mock.patch('select.select', self.select)]
        
    @classmethod
    def get_events_namespace(cls):
        """Return the namespace of the select events."""
        return cls.EVENTS_NAMESPACE
    
    @classmethod
    def get_events_types(cls):
        """Return Enum of select events types."""
        return cls.EventTypes 
        
    @staticmethod
    def _list_intersection(list1, list2):
        return list(set(list1).intersection(set(list2)))
    
    def _get_earliest_events(self, waited_fds, event, timeout):
        added_timeout = float('inf') if timeout is None else timeout
        
        timeout_timestamp = self.clock.time + added_timeout
        
        result_events = []
        result_timestamp = timeout_timestamp

        def _is_relevant_fd_event(fd, evt):
            return fd in waited_fds and evt == event

        # fd_events is a list of [(fd, set(events)), ...].
        for timestamp, fd_events in self.events_pool.get_events(
                _is_relevant_fd_event):
            if timestamp > timeout_timestamp:
                # No event before the timeout
                break
            
            if fd_events:
                result_events = [fd for fd, _ in fd_events]
                result_timestamp = timestamp
                break
            
        return result_timestamp, result_events
    
    def _mocked_select(self, rlist, wlist, xlist, timeout=None):
        read_timestamp, read_fds = self._get_earliest_events(
            rlist,
            self.EventTypes.READ,
            timeout)
        write_timestamp, write_fds = self._get_earliest_events(
            wlist,
            self.EventTypes.WRITE,
            timeout)
        ex_timestamp, ex_fds = self._get_earliest_events(
            xlist,
            self.EventTypes.EXCEPTIONAL,
            timeout)

        timestamp = min([read_timestamp,
                         write_timestamp,
                         ex_timestamp])
        
        if timestamp == float('inf'):
            raise ValueError('No relevant future events were set fot infinite '
                             'timout')
        
        read_fds = [] if timestamp < read_timestamp else read_fds
        write_fds = [] if timestamp < write_timestamp else write_fds
        ex_fds = [] if timestamp < ex_timestamp else ex_fds

        self.events_pool.remove_fds(timestamp,
                                    [(fd, self.EventTypes.READ)
                                     for fd in read_fds])
        self.events_pool.remove_fds(timestamp,
                                    [(fd, self.EventTypes.WRITE)
                                     for fd in write_fds])
        self.events_pool.remove_fds(timestamp,
                                    [(fd, self.EventTypes.EXCEPTIONAL)
                                     for fd in ex_fds])

        self.clock.time = timestamp
    
        return read_fds, write_fds, ex_fds
