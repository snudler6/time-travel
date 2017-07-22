"""Mocking interface for python time libraries."""

from patchers.datetime_patcher import DatetimePatcher
from patchers.time_patcher import TimePatcher
from patchers.select_patcher import SelectPatcher

from time_machine_clock import TimeMachineClock
from events_pool import EventsPool

import sys
print sys.path


class TimeTravel(object):
    """Context-manager patching time libraries.
    
    - For setting timestamps and advancing the time, use the clock object
      corresponiding to the time_machine_clock interface
      
    - For setting events for event based libraies (i.e. select) use the
      events_pool object corresponding to the events_pool interface.
    """
    
    class EventsType(object):
        """Empty class to register events types on."""
    
    def __init__(self, start_time=0):
        """Create the patch.
        
        @start_time is time in seconds since the epoch.
        """
        self.events_pool = EventsPool()
        self.clock = TimeMachineClock(start_time, [self.events_pool])
        
        patches = [DatetimePatcher, TimePatcher, SelectPatcher]
        self.patches = [patcher(self.clock, self.events_pool) for patcher in
                        patches]
        
        self.events_types = TimeTravel.EventsType()
        
        for patcher in self.patches:
            patcher.register_events_types(self.events_types)
   
    def __enter__(self):
        for patcher in self.patches:
            patcher.start()
        
        return self
        
    def __exit__(self, *args):
        for patcher in self.patches:
            patcher.stop()
