"""A single event pool for all patchers."""


class EventsPool(object):
    """Events set """
    
    
    def __init__(self):
        self.future_events = {}
        
    def add_future_event(self, timestamp, event):
        """Add an event to a given timestamp."""
        self.future_events.setdefault(timestamp, set()).add(event)
        
    def get_events(self):
        """Return all added events sorted by timestamp.
        
        
        The returned list is:
        [(timestamp1, set(events)), (timestamp2, set(events)), ....]
        where the timestamps are sorted.
        """
        return sorted(self.future_events.items())
    
    def set_timestamp(self, timestamp):
        """Remove all events before the given timestamp.
        
        This method should be called automatically after signing on the
        TimeMachineClock.
        """
        self.future_events = {k: v for k, v in self.future_events.items()
                              if k >= timestamp}
        
    def remove_events(self, timestamp, events):
        """Remove a list of events from a single timestamp"""
        for event in events:
            self.future_events.get(timestamp, set()).remove(event)