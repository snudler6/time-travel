"""Mocking interface for python time libraries."""

import pkg_resources

from .time_machine_clock import TimeMachineClock, MIN_START_TIME
from .event_pool import EventPool


class TimeTravel(object):
    """Context-manager patching time libraries.
    
    - For setting timestamps and advancing the time, use the clock object
      corresponding to the time_machine_clock interface
      
    - For setting events for event based libraries (e.g. select) use the
      event_pool object corresponding to the event_pool interface.
    """
    
    class EventTypes(object):
        """Empty class to register events types on."""
    
    def __init__(self, start_time=MIN_START_TIME, **kwargs):
        """Create the patch.
        
        @start_time is time in seconds since the epoch.
        """
        self.event_pool = EventPool()
        self.clock = TimeMachineClock(start_time, [self.event_pool])

        patches = [] 
        for patcher in pkg_resources.iter_entry_points(
                group='time_travel.patchers'):
            patches.append(patcher.load())

        self.patches = [patcher(clock=self.clock, event_pool=self.event_pool,
                                **kwargs)
                        for patcher in patches]
        
        self.event_types = self.EventTypes()
        
        for patcher in self.patches:
            if patcher.get_events_namespace() is not None:
                setattr(self.event_types,
                        patcher.get_events_namespace(),
                        patcher.get_event_types())

    def add_future_event(self, time_from_now, fd, event):
        """Add an event to the event pool with a relative timestamp."""
        abs_time = self.clock.time + time_from_now
        self.event_pool.add_future_event(abs_time, fd, event)

    def start(self):
        """Start all the patchers."""
        for patcher in self.patches:
            patcher.start()

    def stop(self):
        """Stop all the patchers."""
        for patcher in self.patches:
            patcher.stop()

    def __enter__(self):
        self.start()
        return self
        
    def __exit__(self, *args):
        self.stop()
