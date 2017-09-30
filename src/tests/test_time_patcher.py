from time_travel.patchers.time_patcher import TimePatcher
from time_travel.time_travel import TimeMachineClock
from .utils import _t

import time


class TestTimePatcher(object):
    
    def setup_method(self, method):
        """Start a time patcher."""
        self.clock = TimeMachineClock()
    
        self.patcher = TimePatcher(clock=self.clock,
                                   event_pool=None,
                                   modules_to_patch=__name__)
        self.patcher.start()
        
    def teardown_method(self, method):
        """Stop the datetime patcher"""
        self.patcher.stop()

    def test_time_patch(self):
        
        assert time.time() == _t(0)
        self.clock.time = _t(3600)
        assert time.time() == _t(3600)
    
    def test_sleep_patch(self):
        assert time.time() == _t(0)
        time.sleep(3600)
        assert time.time() == _t(3600)
        
        self.clock.time = _t(7200)
        assert time.time() == _t(7200)
            
    def test_patcher_stop(self):
        assert time.time() == _t(0)
        
        self.patcher.stop()
        
        assert time.time() != _t(0)
