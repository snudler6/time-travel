"""A single event pool for all patchers."""


class EventsPool(object):
    """Events set for handling patches of event drived libraries."""
    
    def __init__(self):
        """Initialise an event pool."""
        self.future_events = {}
        
    def add_future_event(self, timestamp,
                         event_descriptor,
                         event_predicate=None):
        """Add an event to a given timestamp.
        
        - timestamp: time in seconds since the epoch.
        - event: any object (preferebly mock object) identifying the object
                 that a patched event waiting function will be wait on. 
        """
        self.future_events.setdefault(timestamp, set()).add(
            (event_descriptor, event_predicate))
        
    def get_events(self, predicate=None):
        """Return all added events sorted by timestamp.
        
        The returned list is:
        [(timestamp1, set(events)), (timestamp2, set(events)), ....]
        where the timestamps are sorted.
        """
        def filtered_set(events_set):
            return set([event for event, event_type in
                        events_set if predicate(event_type)])
        
        predicate = (lambda etype: True) if predicate is None else predicate
        
        filterd_events = [(timestamp, filtered_set(events_set)) for
                          timestamp, events_set in self.future_events.items()]
        
        return sorted(filterd_events, key=lambda x: x[0])
    
    def set_timestamp(self, timestamp):
        """Remove all events before the given timestamp.
        
        - timestamp: time in seconds since the epoch.
         
        A callback function for time_machine_clock changes.
        After a time has change, the pool can get rid of events, already
        happened but no called in any patch.
        """
        self.future_events = {k: v for k, v in self.future_events.items()
                              if k >= timestamp}
        
    def remove_events(self, timestamp, events, event_type=None):
        """Remove a list of events from a single timestamp."""
        for event in events:
            self.future_events.get(timestamp, set()).remove(
                (event, event_type))
