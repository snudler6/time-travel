"""Mocking interface for python time libraries."""

from datetime_patcher import DatetimePatcher
from time_patcher import TimePatcher


class TimeMachineClock(object):
    """Unifing class for clock types."""
    
    def __init__(self, start_timestamp=0.0):
        """Initialize a unifing clock."""
        self._timestamp = start_timestamp
        
    def get_timestamp(self):
        """Get the clock timestamp in seconds since the epoch."""
        return self._timestamp
        
    @property
    def timestamp(self):
        """Get the clock timestamp in seconds since the epoch."""
        return self._timestamp
    
    @timestamp.setter
    def timestamp(self, timestatmp):
        """Set the clock timestamp.
        
        @timestamp - is time in seconds since the epoch.
        """
        self._timestamp = float(timestatmp)
    
    def advance_timestamp(self, secs):
        """Advance the clock timestamp since the epoch."""
        self._timestamp += secs
        

class TimeTravel(object):
    """Context-manager patching time libraries."""
    
    def __init__(self, start_time=0):
        """Create the patch.
        
        @start_time is time in seconds since the epoch.
        """
        self.clock = TimeMachineClock(start_time)
        
        self.patches = [DatetimePatcher(self.clock),
                        TimePatcher(self.clock),
                        ]

    def set_time(self, timestamp):
        """Set the time returned by now functions.
        
        @timestamp - is time in seconds since the epoch.
        """
        self.clock.timestamp = timestamp
        
    def get_time(self):
        """Return a datetime object of the currently set time."""
        return self.clock.timestamp
    
    def __enter__(self):
        for patcher in self.patches:
            patcher.start()
        
        return self
        
    def __exit__(self, *args):
        for patcher in self.patches:
            patcher.stop()
