from time_travel.time_patcher import TimePatcher
import time


def test_time_patch():
    with TimePatcher() as t:
        
        assert time.time() == 0
        t.set_time(3600)
        assert time.time() == 3600


def test_sleep_patch():
    with TimePatcher() as t:
        
        assert time.time() == 0
        time.sleep(3600)
        assert time.time() == 3600
        
        t.set_time(7200)
        assert time.time() == 7200
