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
    
    class EventsType(object):
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
        
        self.events_types = TimeTravel.EventsType()
        
        for patcher in self.patches:
            if patcher.get_events_namespace() is not None:
                setattr(self.events_types,
                        patcher.get_events_namespace(),
                        patcher.get_events_types())

    def add_future_event(self, time_from_now, fd, event):
        """Add an event to the event pool with a relative timestamp."""
        self.event_pool.add_future_event(self.clock.time + time_from_now,
                                         fd,
                                         event)
   
    def __enter__(self):
        for patcher in self.patches:
            patcher.start()
        
        return self
        
    def __exit__(self, *args):
        for patcher in self.patches:
            patcher.stop()
