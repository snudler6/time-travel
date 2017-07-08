from time_travel.time_patcher import TimePatcher
import time


def test_time_patch():
    with TimePatcher() as t:
        
        assert time.time() == 0
        t.set_time(3600)
        assert time.time() == 3600
