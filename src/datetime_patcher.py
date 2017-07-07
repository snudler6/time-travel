""""""

import datetime as datetime_lib
from functools import partial
import mock


def lib_name():
    return 'datetime' 


class datetime_patcher(object):
    
    def __init__(self, start_time=0):
        self.timestamp = start_time
        
        self.real_datetime = datetime_lib.datetime.fromtimestamp
        
        self.datetime = mock.Mock(wraps=datetime_lib.datetime)
        self.datetime.mock_add_spec(["today", "now",  "utcnow", "fromtimestamp"])
        
        today_mock = mock.Mock(side_effect=self.get_time)
        self.datetime.today = today_mock

    def set_time(self, timestamp):
        self.timestamp = timestamp
        
    def get_time(self):
        return self.real_datetime(self.timestamp)
    
    def start(self):
        patcher = mock.patch('datetime.datetime', self.datetime)
        patcher.start()

        