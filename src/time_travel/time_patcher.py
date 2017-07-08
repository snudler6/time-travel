"""A patch to the time module."""

import mock


class TimePatcher(object):
    """Context-manager patching the time module.
    
    Patching:
        - time
    """
    
    def __init__(self, start_time=0.0):
        """Create the patch.
        
        @start_time is time in seconds since the epoch.
        """
        self.timestamp = start_time
        
        self.time_patch = mock.patch('time.time', side_effect=self.get_time)
        self.sleep_patch = mock.patch('time.sleep',
                                      side_effect=self.advance_time)
        
    def set_time(self, timestamp):
        """Set the time returned by now functions.
        
        @timestamp - is time in seconds since the epoch.
        """
        self.timestamp = timestamp
        
    def get_time(self):
        """Return a datetime object of the currently set time."""
        return self.timestamp
    
    def advance_time(self, secs):
        """Increase the returned time in a given amount of seconds."""
        self.timestamp += secs
    
    def __enter__(self):
        self.time_patch.start()
        self.sleep_patch.start()
        
        return self
        
    def __exit__(self, _, _, _):
        self.time_patch.stop()
        self.sleep_patch.stop()
