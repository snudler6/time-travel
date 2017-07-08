"""A patch to the datetime module."""

import datetime as datetime_lib
import mock


class DatetimePatcher(object):
    """Context-manager patching the datetime module.
    
    For now patching only the @today function.
    """
    
    def __init__(self, start_time=0):
        """Create the patch.
        
        @start_time is time in seconds since the epoch.
        """
        self.timestamp = start_time
        
        self.real_datetime = datetime_lib.datetime.fromtimestamp
        
        self.datetime = mock.Mock(wraps=datetime_lib.datetime)
        self.datetime.mock_add_spec(
            ["today", "now", "utcnow", "fromtimestamp"])
        
        today_mock = mock.Mock(side_effect=self.get_time)
        self.datetime.today = today_mock
        
        self.datetime_patcher = mock.patch('datetime.datetime', self.datetime)

    def set_time(self, timestamp):
        """Set the time returned by now functions.
        
        @timestamp - is time in seconds since the epoch.
        """
        self.timestamp = timestamp
        
    def get_time(self):
        """Return a datetime object of the currently set time."""
        return self.real_datetime(self.timestamp)
    
    def __enter__(self):
        self.datetime_patcher.start()
        
        return self
        
    def __exit__(self, type, value, traceback):
        self.datetime_patcher.stop()
