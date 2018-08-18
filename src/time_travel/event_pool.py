"""A utility class that holds I/O events and their expiration time."""


class EventPool(object):
    """A pool that holds I/O events and their expiration time.

    The pool holds file descriptors and the events that will occur for them
    for each second since epoch.
    For example, a file descriptor can contain a READABLE and/or a WRITABLE
    event. The event types themselves are defined by the I/O mock class.

    The descriptors are held in a dictionary with the following format:
      self._future_events = {timestamp: {fd: set(event, ...), ...}}
    """

    def __init__(self):
        """Initialize the event pool."""
        self._future_events = {}

    def add_future_event(self, timestamp, fd, event):
        """Add an event to a given timestamp.

        - timestamp: Time in seconds since the epoch.
        - fd: Any object that an I/O function (select, poll, etc.) will be
              waiting on.
        - event: Any object that the relevant patcher can filter the event by.
        """
        ts_dict = self._future_events.setdefault(timestamp, dict())
        fd_set = ts_dict.setdefault(fd, set())
        fd_set.add(event)

    def get_events(self, predicate=None):
        """Return a list of all added events sorted by timestamp.

        - predicate: A condition to filter the fds ane events by.
                     The predicate will be checked on the (fd, event) tuple.

        The returned list is in the following format (and sorted by timestamp):
          [(timestamp, [(fd, set(events)), ...]), ...]
        """
        predicate = (lambda fd, evt: True) if predicate is None else predicate

        def _filter(_ts_dict):
            """Return fd and events subset matching to the predicate."""
            out = []

            for fd, event_set in _ts_dict.items():
                out_events = set()
                for event in event_set:
                    if predicate(fd, event):
                        out_events.add(event)

                if out_events:
                    out.append((fd, out_events))

            return out

        filtered_events = []
        for timestamp, ts_dict in self._future_events.items():
            filtered_events_for_ts = _filter(ts_dict)
            if filtered_events_for_ts:
                filtered_events.append((timestamp, filtered_events_for_ts))

        return sorted(filtered_events, key=lambda x: x[0])

    def get_next_event(self, predicate=None):
        """Return the next event to occur.

        The returned evens it a tuple of (timestamp, [(fd, set(events)), ...]).
        """
        events = self.get_events(predicate)
        return (None, []) if not events else events[0]

    def set_time(self, timestamp):
        """Remove all events before the given timestamp.

        - timestamp: Time in seconds since the epoch.

        This method ia a callback function for `time_machine_clock` changes.
        After the time has changed, the pool can throw away older events that
        had already satisfied.
        """
        self._future_events = {k: v for k, v in self._future_events.items()
                               if k >= timestamp}

    def remove_event_from_fd(self, timestamp, fd, event):
        """Remove a single event for a single fd from a single timestamp.

        If the fd has no more events for it after the removal - removes the fd
        from the timestamp dict.

        If the timestamp has no more fd entries in it after the removal -
        removes the timestamp from `future_events`.
        """
        self._future_events[timestamp][fd].remove(event)

        if not self._future_events[timestamp][fd]:
            self._future_events[timestamp].pop(fd)

        if not self._future_events[timestamp]:
            self._future_events.pop(timestamp)

    def remove_events_from_fds(self, timestamp, fd_events):
        """Remove a list of [(fd, event), ...] from a single timestamp."""
        for fd, event in fd_events:
            self.remove_event_from_fd(timestamp, fd, event)
