"""A patch to the select.poll object."""

from .base_patcher import BasePatcher

import select as select_lib


class MockPollObject(object):
    """A mock poll object."""

    def __init__(self, clock, event_pool):
        """Initialize the object."""
        self.clock = clock
        self.event_pool = event_pool

        self.poll_events = {}

    def register(self, fd, eventmask=None):
        """Register a file descriptor with the fake polling object."""
        if eventmask is None:
            eventmask = (select_lib.POLLIN |
                         select_lib.POLLOUT |
                         select_lib.POLLPRI)
        self.poll_events[fd] = eventmask

    def modify(self, fd, eventmask):
        """Modify an already registered fd's event mask."""
        if fd not in self.poll_events:
            raise IOError()

        self.poll_events[fd] = eventmask

    def unregister(self, fd):
        """Remove a file descriptor tracked by the fake polling object."""
        if fd not in self.poll_events:
            raise KeyError(fd)

        self.poll_events.pop(fd)

    def poll(self, timeout=None):
        """Poll the set of registered file descriptors.

        `timeout` is a value in milliseconds.
        """
        timestamp, fd_events = \
            self._get_earliest_events_for_waited_fds(timeout)

        if timestamp == float('inf'):
            raise ValueError('No relevant future events were set for infinite '
                             'timout')

        for fd, events in fd_events:
            self.event_pool.remove_events_from_fds(
                timestamp,
                [(fd, event) for event in events])

        self.clock.time = timestamp

        def _crunch_events(_event_set):
            out = 0
            for _event in _event_set:
                out |= _event
            return out

        return [(fd, _crunch_events(events)) for fd, events in fd_events]

    def _get_earliest_events_for_waited_fds(self, timeout=None):
        """Return a list of [(fd, set(events)), ...]."""
        if timeout is None or timeout < 0:
            timeout = float('inf')
        else:
            timeout = timeout / 1000.0

        timeout_timestamp = self.clock.time + timeout

        def _is_relevant_fd_event(fd, evt):
            return fd in self.poll_events and self.poll_events[fd] & evt

        # fd_events is a list of [(fd, set(events)), ...].
        ts, fd_events = self.event_pool.get_next_event(_is_relevant_fd_event)

        if ts is None or ts > timeout_timestamp:
            return timeout_timestamp, []
        else:
            return ts, fd_events


class PollPatcher(BasePatcher):
    """Patcher for select.poll."""

    def __init__(self, *args, **kwargs):
        """Create the patch."""
        super(PollPatcher, self).__init__(*args, **kwargs)

    def get_patched_module(self):
        """Return the actual module obect to be patched."""
        return select_lib

    def get_patch_actions(self):
        """Return generator containing all patches to do."""
        return [('poll', select_lib.poll, self._mock_poll)]

    def _mock_poll(self):
        return MockPollObject(self.clock, self.event_pool)
