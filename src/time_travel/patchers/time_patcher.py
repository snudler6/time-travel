"""A patch to the time module."""

from .base_patcher import BasePatcher

import mock
import time


class TimePatcher(BasePatcher):
    """Patcher of the time module.
    
    Patching:
        - time
        - sleep
    """
    
    def __init__(self, **kwargs):
        """Create the patch."""
        super(TimePatcher, self).__init__(patcher_module=__name__, **kwargs)
        
    def get_patched_module(self):
        """Do more stuff."""
        return time
        
    def get_patch_actions(self):
        """Return generator containing all patches to do."""
        return [
            ('time', time.time, mock.Mock(side_effect=self._get_timestamp)),
            ('sleep', time.sleep,
             mock.Mock(side_effect=self._advance_time_stamp))
        ]
    
    def _get_timestamp(self):
        """Return the clock timestamp.
        
        Used for mocks side_effect, not to pre-evaluate the time property.
        """
        return self.clock.time
    
    def _advance_time_stamp(self, seconds):
        """Return the clock time.
        
        Used for the side_effect of sleep.
        """
        self.clock.time += seconds
