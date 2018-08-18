"""Mocking interface for python time libraries."""

import pkg_resources

from .time_machine_clock import TimeMachineClock, MIN_START_TIME
from .event_pool import EventPool


class TimeTravel(object):
    """Context-manager for patching time and I/O libraries."""

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
        """Add an event to the event pool.

        :param time_from_now: When will the event happen.
        :param fd: The descriptor (usually a socket object) that the event will
                   happen for.
        :param event: The event that will happen (implementation specific).
        """
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
