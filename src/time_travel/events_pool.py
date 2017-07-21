"""A single event pool for all patchers."""


class EventsPool(object):
    """Events set for handling patches of event drived libraries."""
    
    def __init__(self):
        """Initialise an event pool."""
        self.future_events = {}
        
    def add_future_event(self, timestamp, event):
        """Add an event to a given timestamp.
        
        - timestamp: time in seconds since the epoch.
        - event: any object (preferebly mock object) identifying the object
                 that a patched event waiting function will be wait on. 
        """
        self.future_events.setdefault(timestamp, set()).add(event)
        
    def get_events(self):
        """Return all added events sorted by timestamp.
        
        The returned list is:
        [(timestamp1, set(events)), (timestamp2, set(events)), ....]
        where the timestamps are sorted.
        """
        return sorted(self.future_events.items(), key=lambda x: x[0])
    
    def set_timestamp(self, timestamp):
        """Remove all events before the given timestamp.
        
        - timestamp: time in seconds since the epoch.
         
        A callback function for time_machine_clock changes.
        After a time has change, the pool can get rid of events, already
        happened but no called in any patch.
        """
        self.future_events = {k: v for k, v in self.future_events.items()
                              if k >= timestamp}
        
    def remove_events(self, timestamp, events):
        """Remove a list of events from a single timestamp."""
        for event in events:
            self.future_events.get(timestamp, set()).remove(event)
