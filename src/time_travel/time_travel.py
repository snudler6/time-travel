"""Mocking interface for python time libraries."""

import pkg_resources

from .time_machine_clock import TimeMachineClock, MIN_START_TIME
from .events_pool import EventsPool


class TimeTravel(object):
    """Context-manager patching time libraries.
    
    - For setting timestamps and advancing the time, use the clock object
      corresponiding to the time_machine_clock interface
      
    - For setting events for event based libraies (i.e. select) use the
      events_pool object corresponding to the events_pool interface.
    """
    
    class EventsType(object):
        """Empty class to register events types on."""
    
    def __init__(self, start_time=MIN_START_TIME, **kwargs):
        """Create the patch.
        
        @start_time is time in seconds since the epoch.
        """
        self.events_pool = EventsPool()
        self.clock = TimeMachineClock(start_time, [self.events_pool])

        patches = [] 
        for patcher in pkg_resources.iter_entry_points(
                group='time_travel.patchers'):
            patches.append(patcher.load())

        self.patches = [patcher(clock=self.clock, events_pool=self.events_pool,
                                **kwargs)
                        for patcher in patches]
        
        self.events_types = TimeTravel.EventsType()
        
        for patcher in self.patches:
            if patcher.get_events_namespace() is not None:
                setattr(self.events_types,
                        patcher.get_events_namespace(),
                        patcher.get_events_types())
   
    def __enter__(self):
        for patcher in self.patches:
            patcher.start()
        
        return self
        
    def __exit__(self, *args):
        for patcher in self.patches:
            patcher.stop()
