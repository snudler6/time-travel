"""A patch to the datetime module."""

from .basic_patcher import BasicPatcher

import datetime as datetime_lib
import mock


real_datetime_class = datetime_lib.datetime


class DatetimePatcher(BasicPatcher):
    """Patcher of the datetime module.
    
    patching:
        - datetime.today
        - datetime.now
        - datetime.utcnow
    """
    
    class DatetimeSubclassMeta(type):
        """Datetime mock metaclass to check instancechek to the real class."""
        
        @classmethod
        def __instancecheck__(mcs, obj):
            return isinstance(obj, real_datetime_class)

    class BaseMockedDatetime(real_datetime_class, mock.Mock):
        """Mock class to cover datetime class."""
        
        @classmethod
        def now(cls, tz=None):
            """Return the current local date and time."""
            return cls._now().replace(tzinfo=tz)

        @classmethod
        def utcnow(cls):
            """Return the current UTC date and time."""
            return cls._now()
        
        @classmethod
        def today(cls):
            """Return the current local date and time."""
            return cls._now()
    
    def __init__(self, *args, **kwargs):
        """Create the patch."""
        super(DatetimePatcher, self).__init__(*args, **kwargs)
        
        MockedDatetime = self.DatetimeSubclassMeta('datetime',
                                                   (self.BaseMockedDatetime,),
                                                   {'_now': self._now})

        patcher = mock.patch('datetime.datetime',
                             MockedDatetime)
               
        self.patches = [
            patcher,
        ]
    
    def _now(self):
        return real_datetime_class.fromtimestamp(self.clock.time)
