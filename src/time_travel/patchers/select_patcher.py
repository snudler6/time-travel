"""A patch to the datetime module."""

from basic_patcher import BasicPatcher

import select as select_lib
import mock


class SelectPatcher(BasicPatcher):
    """Patcher of the datetime module.
    
    patching:
        - datetime.today
    """
    
    def __init__(self, *args, **kwargs):
        """Create the patch."""
        super(SelectPatcher, self).__init__(*args, **kwargs)
        
        self.select = mock.Mock(
            side_effect=self._mocked_select,
            spec=select_lib.select)
        
        self.patches = [mock.patch('select.select', self.select)]
                        
    def _mocked_select(self, rlist, wlist, xlist, timeout=None):
        waited_events = set(rlist + wlist + xlist)
        
        added_timeout = timeout
        if timeout is None:
            added_timeout = float('inf')
        
        timeout_timestamp = self.clock.timestamp + added_timeout
        
        result_events = []
        result_timestamp = timeout_timestamp
        
        for timestamp, events in self.events_pool.get_events():
            if timestamp > timeout_timestamp:
                # No event before the timeout
                break
            
            triggering_events = waited_events.intersection(events) 
            
            if len(triggering_events) != 0:
                result_events = list(triggering_events)
                result_timestamp = timestamp
                break

        if timeout is None and len(result_events) == 0:
            raise ValueError('No relevant future events were set fot infinite '
                             'timout')

        self.events_pool.remove_events(result_timestamp, result_events)

        self.clock.timestamp = result_timestamp
        return result_events
