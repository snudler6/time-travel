from time_travel.patchers.time_patcher import TimePatcher
from time_travel.time_travel import TimeMachineClock

import time


def test_time_patch():
    clock = TimeMachineClock()
    
    patcher = TimePatcher(clock)
    patcher.start()
    
    assert time.time() == 0
    clock.time = 3600
    assert time.time() == 3600
    
    patcher.stop()


def test_sleep_patch():
    clock = TimeMachineClock()
    
    patcher = TimePatcher(clock)
    patcher.start()

    assert time.time() == 0
    time.sleep(3600)
    assert time.time() == 3600
    
    clock.time = 7200
    assert time.time() == 7200

    patcher.stop()

        
def test_patcher_stop():
    clock = TimeMachineClock()
    patcher = TimePatcher(clock)
    patcher.start()
    
    assert time.time() == 0
    
    patcher.stop()
    
    assert time.time() != 0
