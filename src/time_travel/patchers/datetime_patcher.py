"""A patch to the datetime module."""

from basic_patcher import BasicPatcher

import datetime as datetime_lib
import mock


class DatetimePatcher(BasicPatcher):
    """Patcher of the datetime module.
    
    patching:
        - datetime.today
    """
    
    def __init__(self, *args, **kwargs):
        """Create the patch."""
        super(DatetimePatcher, self).__init__(*args, **kwargs)
        
        self.datetime = mock.Mock(wraps=datetime_lib.datetime)
        self.datetime.mock_add_spec(
            ["today", "now", "utcnow", "fromtimestamp"])
        
        self.datetime.today = mock.Mock(side_effect=self._now)
        
        self.patches = [mock.patch('datetime.datetime', self.datetime),
                        ]
        
    def _now(self):
        return self.datetime.fromtimestamp(self.clock.time)
