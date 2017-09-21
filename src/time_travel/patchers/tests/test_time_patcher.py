from time_travel.patchers.time_patcher import TimePatcher
from time_travel.time_travel import TimeMachineClock

import time


def test_time_patch():
    clock = TimeMachineClock()
    
    patcher = TimePatcher(clock)
    patcher.start()
    
    assert time.time() == 100000
    clock.time = 103600
    assert time.time() == 103600
    
    patcher.stop()


def test_sleep_patch():
    clock = TimeMachineClock()
    
    patcher = TimePatcher(clock)
    patcher.start()

    assert time.time() == 100000
    time.sleep(3600)
    assert time.time() == 103600
    
    clock.time = 107200
    assert time.time() == 107200

    patcher.stop()

        
def test_patcher_stop():
    clock = TimeMachineClock()
    patcher = TimePatcher(clock)
    patcher.start()
    
    assert time.time() == 100000
    
    patcher.stop()
    
    assert time.time() != 100000
