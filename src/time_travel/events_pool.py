"""A single event pool for all patchers."""


class EventsPool(object):
    """Events set for handling patches of event derived libraries.

    The pool contains a dictionary that for each second since epoc holds
    file descriptors and the events that will occur for them.
    The dictionary's format is as follows:
      self.future_events = {timestamp: {fd: set(event, ...), ...}}
    """

    def __init__(self):
        """Initialise an event pool."""
        self.future_events = {}
        
    def add_future_event(self, timestamp, fd, event):
        """Add an event to a given timestamp.
        
        - timestamp: time in seconds since the epoch.
        - fd: any object (preferebly mock object) identifying the object that
              a patched event waiting function will be waiting on.
        - event: any object the relevant patcher will filter by.
        """
        ts_dict = self.future_events.setdefault(timestamp, dict())
        fd_set = ts_dict.setdefault(fd, set())
        fd_set.add(event)
        
    def get_events(self, predicate=None):
        """Return all added events sorted by timestamp.
        
        - predicate: A condition to filter the events by. The condition will
                     be activated on the `event` passed to `add_future_event`.
                     
        The returned list is:
        [(timestamp1, [(fd, set(events)), ...]),
         (timestamp2, [(fd, set(events)), ...]), ...]
        where the timestamps are sorted.
        """
        predicate = (lambda fd, evt: True) if predicate is None else predicate
        
        def _filter(_ts_dict):
            """Return fd and events subset matching to the predicate."""
            out = []

            for fd, event_set in _ts_dict.items():
                fd_set = set()
                for event in event_set:
                    if predicate(fd, event):
                        fd_set.add(event)

                if fd_set:
                    out.append((fd, fd_set))

            return out

        filtered_events = []
        for timestamp, ts_dict in self.future_events.items():
            filtered_events_for_ts = _filter(ts_dict)
            if filtered_events_for_ts:
                filtered_events.append((timestamp, filtered_events_for_ts))
        
        return sorted(filtered_events, key=lambda x: x[0])

    def get_next_event(self, predicate=None):
        """Return the next event to occur."""
        events = self.get_events(predicate)
        return (None, []) if not events else events[0]

    def set_time(self, timestamp):
        """Remove all events before the given timestamp.
        
        - timestamp: time in seconds since the epoch.
         
        A callback function for time_machine_clock changes.
        After a time has change, the pool can get rid of events, already
        happened but no called in any patch.
        """
        self.future_events = {k: v for k, v in self.future_events.items()
                              if k >= timestamp}
        
    def remove_event_from_fd(self, timestamp, fd, event):
        """Remove a single event for a single fd from a single timestamp.

        If the fd has no more events for it after the removal - removes the fd
        from the timestamp dict.

        If the timestamp has no more fd entries in it after the removal -
        removes the timestamp from `future_events`.
        """
        self.future_events[timestamp][fd].remove(event)

        if not self.future_events[timestamp][fd]:
            self.future_events[timestamp].pop(fd)

        if not self.future_events[timestamp]:
            self.future_events.pop(timestamp)

    def remove_events_from_fds(self, timestamp, fd_events):
        """Remove a list of [(fd, event), ...] from a single timestamp."""
        for fd, event in fd_events:
            self.remove_event_from_fd(timestamp, fd, event)
