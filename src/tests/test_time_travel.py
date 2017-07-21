from time_travel import TimeTravel

import time
from datetime import datetime


def test_time_patch_set_time():
    with TimeTravel() as t:
        
        assert time.time() == 0
        t.set_time(3600)
        assert time.time() == 3600


def test_sleep_patch_sleep():
    with TimeTravel() as t:
        
        assert time.time() == 0
        time.sleep(3600)
        assert time.time() == 3600
        
        t.set_time(7200)
        assert time.time() == 7200
        
        
def test_datetime_patch_set_time():
    with TimeTravel() as t:
        
        assert datetime.today() == datetime.fromtimestamp(0)
        t.set_time(3600)
        assert datetime.today() == datetime.fromtimestamp(3600)
        

def test_sleep_changing_today():
    with TimeTravel():
        assert datetime.today() == datetime.fromtimestamp(0)
        
        time.sleep(3600)
        assert datetime.today() == datetime.fromtimestamp(3600)
