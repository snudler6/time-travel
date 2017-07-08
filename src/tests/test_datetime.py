from time_travel.datetime_patcher import DatetimePatcher
import datetime


def test_datetime_patch():
    with DatetimePatcher() as t:
        
        print datetime.datetime.today()
        t.set_time(3600)
        print datetime.datetime.today()
        print datetime.datetime.fromtimestamp(7200)
        
        print datetime.datetime(2017, 7, 19)
