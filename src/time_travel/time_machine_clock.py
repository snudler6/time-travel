"""A single clock for all patchers."""


class TimeMachineClock(object):
    """Unifing class for clock types."""
    
    def __init__(self, start_timestamp=0.0, clock_listeners=[]):
        """Initialize a unifing clock."""
        self._timestamp = start_timestamp
        self._clock_listeners = clock_listeners
        
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
        
        for listener in self._clock_listeners:
            listener.set_timestamp(self._timestamp)
    
    def advance_timestamp(self, secs):
        """Advance the clock's timestamp in seconds."""
        self._timestamp += secs
        