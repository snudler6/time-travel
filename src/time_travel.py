"""
"""


import mock
import datetime as lib_datetime
import time as lib_time
from datetime_patcher import datetime_patcher
from time_patcher import time_patcher


class time_travel(object):
    """classdocs"""


    def __init__(self):
        """Constructor"""
        self.time = 0
        datetime_patch = mock.patch('datetime.datetime', datetime_patcher)
        time_patch = mock.patch('datetime.datetime', time_patcher)
        
    def
        