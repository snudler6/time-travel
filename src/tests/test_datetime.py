from time_travel.datetime_patcher import DatetimePatcher
from time_travel.time_travel import TimeMachineClock

import datetime


real_fromtimestamp = datetime.datetime.fromtimestamp


def test_datetime_patch():
    clock = TimeMachineClock()
    with DatetimePatcher(clock):
        assert datetime.datetime.today() == real_fromtimestamp(0)
        
        clock.timestamp = 3600
        assert datetime.datetime.today() == real_fromtimestamp(3600)


def test_patch_not_covering_classmethods():
    assert datetime.datetime.fromtimestamp(0) == real_fromtimestamp(0)
    assert datetime.datetime.fromtimestamp(3600) == real_fromtimestamp(3600)
