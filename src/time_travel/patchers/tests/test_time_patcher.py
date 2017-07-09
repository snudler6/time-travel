from time_travel.patchers.time_patcher import TimePatcher
from time_travel.time_travel import TimeMachineClock

import time


def test_time_patch():
    clock = TimeMachineClock()
    
    with TimePatcher(clock):
        assert time.time() == 0
        clock.timestamp = 3600
        assert time.time() == 3600


def test_sleep_patch():
    clock = TimeMachineClock()
    
    with TimePatcher(clock):
        assert time.time() == 0
        time.sleep(3600)
        assert time.time() == 3600
        
        clock.timestamp = 7200
        assert time.time() == 7200
