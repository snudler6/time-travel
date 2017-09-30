"""A patch to the time module."""

from .base_patcher import BasePatcher

import mock


class TimePatcher(BasePatcher):
    """Patcher of the time module.
    
    Patching:
        - time
        - sleep
    """
    
    def __init__(self, *args, **kwargs):
        """Create the patch."""
        super(TimePatcher, self).__init__(*args, **kwargs)
        
    def get_patches(self):
        """Return generator containing all patches to do."""
        yield ('time.time', mock.Mock(side_effect=self._get_timestamp))
        yield ('time.sleep', mock.Mock(side_effect=self._advance_time_stamp))
    
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
