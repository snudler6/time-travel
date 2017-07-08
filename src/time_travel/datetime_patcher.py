"""A patch to the datetime module."""

import datetime as datetime_lib

import mock
from functools import partial


class DatetimePatcher(object):
    """Context-manager patching the datetime module.
    
    For now patching only the @today function.
    """
    
    def __init__(self, clock):
        """Create the patch.
        
        @start_time is time in seconds since the epoch.
        """
        self.clock = clock
        
        self.real_fromtimestamp = datetime_lib.datetime.fromtimestamp
        
        self.datetime = mock.Mock(wraps=datetime_lib.datetime)
        self.datetime.mock_add_spec(
            ["today", "now", "utcnow", "fromtimestamp"])
        
        self.datetime.today = mock.Mock(side_effect=self._now)
        
        self.patches = [mock.patch('datetime.datetime', self.datetime),
                        ]
        
    def _now(self):
        return self.real_fromtimestamp(self.clock.get_timestamp())
    
    def start(self):
        """Start mocking datetime module."""
        for p in self.patches:
            p.start()
            
    def stop(self):
        """Stop mocking datetime module."""
        for p in self.patches:
                p.stop()
                
    def __enter__(self):
        self.start()
        return self
        
    def __exit__(self, *args):
        self.stop()
