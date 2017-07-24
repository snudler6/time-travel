"""A patch to the time module."""

from basic_patcher import BasicPatcher

import mock


class TimePatcher(BasicPatcher):
    """Patcher of the time module.
    
    Patching:
        - time
        - sleep
    """
    
    def __init__(self, *args, **kwargs):
        """Create the patch."""
        super(TimePatcher, self).__init__(*args, **kwargs)
        
        self.patches.append(
            mock.patch('time.time', side_effect=self._get_timestamp))
        
        self.patches.append(
            mock.patch('time.sleep', side_effect=self._advance_time_stamp))
    
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
