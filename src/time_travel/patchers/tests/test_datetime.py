from time_travel.patchers.datetime_patcher import DatetimePatcher
from time_travel.time_travel import TimeMachineClock

import datetime


class TestDatetimePatcher(object):
    
    def setup_method(self, method):
        """Start a datetime patcher."""
        self.clock = TimeMachineClock()
        self.patcher = DatetimePatcher(self.clock)
        self.patcher.start()
        
    def teardown_method(self, method):
        """Stop the datetime patcher"""
        self.patcher.stop()

    def test_datetime_today(self):
        assert datetime.datetime.today() == datetime.datetime.fromtimestamp(0)
        
        self.clock.time = 3600
        assert datetime.datetime.today() ==\
            datetime.datetime.fromtimestamp(3600)
            
    def test_datetime_utcnow(self):
        assert datetime.datetime.utcnow() == datetime.datetime.fromtimestamp(0)
        
        self.clock.time = 3600
        assert datetime.datetime.utcnow() ==\
            datetime.datetime.fromtimestamp(3600)
            
    def test_datetime_now(self):
        assert datetime.datetime.now() == datetime.datetime.fromtimestamp(0)
        
        self.clock.time = 3600
        assert datetime.datetime.now() ==\
            datetime.datetime.fromtimestamp(3600)
            
    def test_isinstance_works(self):
        from datetime import datetime
        assert isinstance(datetime.today(), datetime)
