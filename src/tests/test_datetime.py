from time_travel.patchers.datetime_patcher import DatetimePatcher
from time_travel.time_travel import TimeMachineClock

import datetime
from datetime import datetime as orig_datetime_class
from .utils import _t


class TestDatetimePatcher(object):
    
    def setup_method(self, method):
        """Start a datetime patcher."""
        self.clock = TimeMachineClock()
        self.patcher = DatetimePatcher(clock=self.clock,
                                       event_pool=None,
                                       modules_to_patch=__name__)
        self.patcher.start()
        
    def teardown_method(self, method):
        """Stop the datetime patcher"""
        self.patcher.stop()

    def test_datetime_today(self):
        assert datetime.datetime.today() == \
            datetime.datetime.fromtimestamp(_t(0))
        
        self.clock.time = _t(3600)
        assert datetime.datetime.today() == \
            datetime.datetime.fromtimestamp(_t(3600))
            
    def test_datetime_utcnow(self):
        assert datetime.datetime.utcnow() == \
            datetime.datetime.fromtimestamp(_t(0))
        
        self.clock.time = _t(3600)
        assert datetime.datetime.utcnow() == \
            datetime.datetime.fromtimestamp(_t(3600))
            
    def test_datetime_now(self):
        assert datetime.datetime.now() == \
            datetime.datetime.fromtimestamp(_t(0))
        
        self.clock.time = _t(3600)
        assert datetime.datetime.now() == \
            datetime.datetime.fromtimestamp(_t(3600))
            
    def test_isinstance_works(self):
        assert isinstance(datetime.datetime.today(),
                          orig_datetime_class)
