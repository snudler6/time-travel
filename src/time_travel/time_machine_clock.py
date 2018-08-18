"""A single clock for all patchers."""


MIN_START_TIME = 86400.0  # Windows support unix times starting from 86,400.


class TimeMachineClock(object):
    """Unifing class for clock types."""

    def __init__(self, start_time=MIN_START_TIME, clock_listeners=None):
        """Initialise a unified clock."""
        if start_time < MIN_START_TIME:
            raise ValueError('start_time cannot be lower than {} ({} given)'.
                             format(MIN_START_TIME, start_time))

        self._time = start_time

        self._clock_listeners = clock_listeners
        if clock_listeners is None:
            self._clock_listeners = []

    @property
    def time(self):
        """Get the clock time in seconds since the epoch."""
        return self._time

    @time.setter
    def time(self, time):
        """Set the clock time.

        time - is time in seconds since the epoch.
        """
        self._time = float(time)

        for listener in self._clock_listeners:
            listener.set_time(self._time)
