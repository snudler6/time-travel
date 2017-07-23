"""A single event pool for all patchers."""


class EventsPool(object):
    """Events set for handling patches of event drived libraries."""
    
    def __init__(self):
        """Initialise an event pool."""
        self.future_events = {}
        
    def add_future_event(self,
                         timestamp,
                         event_descriptor,
                         event_predicate=None):
        """Add an event to a given timestamp.
        
        - timestamp: time in seconds since the epoch.
        - event_descriptor: any object (preferebly mock object) identifying the
                            object that a patched event waiting function will
                            be wait on.
        - event_predicate: any object the relevant patcher will filter by.
        """
        self.future_events.setdefault(timestamp, set()).add(
            (event_descriptor, event_predicate))
        
    def get_events(self, predicate=None):
        """Return all added events sorted by timestamp.
        
        - predicate: A condition to filter the events by. The condition will
                     be activated on the event_predicate passed to
                     `add_future_event`
                     
        The returned list is:
        [(timestamp1, set(events)), (timestamp2, set(events)), ....]
        where the timestamps are sorted.
        """
        predicate = (lambda etype: True) if predicate is None else predicate
        
        def _filtered_set(events_set):
            """Return evevnts subset matching to the predicate.
            
            Also remove the event type from the event tuple.
            """
            return set([event for event, event_type in
                        events_set if predicate(event_type)])
        
        filterd_events = [(timestamp, _filtered_set(events_set)) for
                          timestamp, events_set in self.future_events.items()]
        
        return sorted(filterd_events, key=lambda x: x[0])
    
    def set_time(self, timestamp):
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
            self.future_events[timestamp].remove((event, event_type))
        
        if events and not self.future_events[timestamp]:
            self.future_events.pop(timestamp)
