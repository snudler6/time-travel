"""Mocking interface for python time libraries"""

from datetime_patcher import DatetimePatcher
from time_patcher import TimePatcher

class TimeTravel(object):
    """Context-manager patching time libraries."""
    
    def __init__(self, start_time=0):
        """Create the patch.
        
        @start_time is time in seconds since the epoch.
        """
        self.timestamp = start_time
        
        self.patches = [DatetimePatcher(start_time),
                        TimePatcher(start_time),
                        ]

    def set_time(self, timestamp):
        """Set the time returned by now functions.
        
        @timestamp - is time in seconds since the epoch.
        """
        self.timestamp = timestamp
        for patcher in self.patches:
            patcher.set_time(timestamp)
        
    def get_time(self):
        """Return a datetime object of the currently set time."""
        return self.timestamp
    
    def __enter__(self):
        for patcher in self.patches:
            patcher.start()
        
        return self
        
    def __exit__(self, _, _, _):
        for patcher in self.patches:
            patcher.stop()
