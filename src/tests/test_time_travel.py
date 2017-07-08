from time_travel.time_travel import TimeTravel

import time
import datetime


real_fromtimestamp = datetime.datetime.fromtimestamp


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
        
        print datetime.datetime.today()
        t.set_time(3600)
        print datetime.datetime.today()
        print datetime.datetime.fromtimestamp(7200)
        
        print datetime.datetime(2017, 7, 19)
        

def test_sleep_changing_today():
    with TimeTravel():
        assert datetime.datetime.today() == real_fromtimestamp(0)
        
        time.sleep(3600)
        assert datetime.datetime.today() == real_fromtimestamp(3600)
