"""A patch to the select.select function."""

from .base_patcher import BasePatcher

import select as select_lib
from enum import Enum


class SelectPatcher(BasePatcher):
    """Patcher for select.select."""

    EVENTS_NAMESPACE = 'select'
    EventTypes = Enum('select', ['READ', 'WRITE', 'EXCEPTIONAL'])

    def __init__(self, *args, **kwargs):
        """Create the patch."""
        super(SelectPatcher, self).__init__(*args, **kwargs)

    def get_patch_actions(self):
        """Return generator containing all patches to do."""
        return [('select', select_lib.select, self._mocked_select)]

    def get_patched_module(self):
        """Return the actual module obect to be patched."""
        return select_lib

    @classmethod
    def get_events_namespace(cls):
        """Return the namespace of the select events."""
        return cls.EVENTS_NAMESPACE

    @classmethod
    def get_event_types(cls):
        """Return Enum of select events types."""
        return cls.EventTypes

    @staticmethod
    def _list_intersection(list1, list2):
        return list(set(list1).intersection(set(list2)))

    def _get_earliest_events(self, waited_fds, event, timeout):
        added_timeout = float('inf') if timeout is None else timeout

        timeout_timestamp = self.clock.time + added_timeout

        def _is_relevant_fd_event(fd, evt):
            return fd in waited_fds and evt == event

        # fd_events is a list of [(fd, set(events)), ...].
        ts, fd_events = self.event_pool.get_next_event(
            _is_relevant_fd_event)

        if ts is None or ts > timeout_timestamp:
            return timeout_timestamp, []
        else:
            return ts, [fd for fd, _ in fd_events]

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
            raise ValueError('No relevant future events were set for infinite '
                             'timout')

        read_fds = [] if timestamp < read_timestamp else read_fds
        write_fds = [] if timestamp < write_timestamp else write_fds
        ex_fds = [] if timestamp < ex_timestamp else ex_fds

        self.event_pool.remove_events_from_fds(
            timestamp,
            [(fd, self.EventTypes.READ) for fd in read_fds])
        self.event_pool.remove_events_from_fds(
            timestamp,
            [(fd, self.EventTypes.WRITE) for fd in write_fds])
        self.event_pool.remove_events_from_fds(
            timestamp,
            [(fd, self.EventTypes.EXCEPTIONAL) for fd in ex_fds])

        self.clock.time = timestamp

        return read_fds, write_fds, ex_fds
