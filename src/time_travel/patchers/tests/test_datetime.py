from time_travel.patchers.datetime_patcher import DatetimePatcher
from time_travel.time_travel import TimeMachineClock

import datetime


def test_datetime_patch():
    clock = TimeMachineClock()
    patcher = DatetimePatcher(clock)
    patcher.start()
    
    assert datetime.datetime.today() == datetime.datetime.fromtimestamp(0)
    
    clock.time = 3600
    assert datetime.datetime.today() == datetime.datetime.fromtimestamp(3600)
    patcher.stop()
    
    
def test_patcher_stop():
    clock = TimeMachineClock()
    patcher = DatetimePatcher(clock)
    patcher.start()
    
    assert datetime.datetime.today() == datetime.datetime.fromtimestamp(0)
    
    patcher.stop()
    
    assert datetime.datetime.today() != datetime.datetime.fromtimestamp(0)
