"""A patch to the time module."""

from basic_patcher import BasicPatcher

import mock


class TimePatcher(BasicPatcher):
    """Patcher of the time module.
    
    Patching:
        - time
        - sleep
    """
    
    def __init__(self, clock):
        """Create the patch."""
        super(TimePatcher, self).__init__(clock)
        
        self.patches.append(
            mock.patch('time.time', side_effect=self._get_timestamp))
        self.patches.append(
            mock.patch('time.sleep', side_effect=self.clock.advance_timestamp))
    
    def _get_timestamp(self):
        """Return the clock timestamp.
        
        Used for mocks side_effect, not to pre-evaluate the timestamp property.
        """
        return self.clock.timestamp
