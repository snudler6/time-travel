"""A patch to the datetime module."""

from .basic_patcher import BasicPatcher

import datetime
from dateutil.tz import tzlocal

try:
    import copy_reg as copyreg
except ImportError:
    import copyreg


real_datetime = datetime.datetime
real_date = datetime.date


def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    return meta("NewBase", bases, {})


class DatetimeSubclassMeta(type):
    """Datetime mock metaclass to check instancechek to the real class."""
    
    @classmethod
    def __instancecheck__(mcs, obj):
        return isinstance(obj, real_datetime)
    
    
class BaseMockedDate(real_date):
    """Mock class to cover date class."""
    
    @classmethod
    def today(cls):
        """Return the current local date and time."""
        return cls._now()


class DateSubclassMeta(type):
    """Date mock metaclass to check instancechek to the real class."""
    
    @classmethod
    def __instancecheck__(mcs, obj):
        return isinstance(obj, real_date)


class BaseMockedDatetime(real_datetime):
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


MockedDatetime = DatetimeSubclassMeta(
    'datetime',
    (BaseMockedDatetime,),
    {})

MockedDate = DateSubclassMeta(
    'date',
    (BaseMockedDate,),
    {})


class FakeDateMeta(type):
    """Add here a better docstring."""
    
    @classmethod
    def __instancecheck__(self, obj):
        """Add here a better docstring."""
        return isinstance(obj, real_date)


def datetime_to_fakedatetime(datetime):
    """Add here a better docstring."""
    return FakeDatetime(datetime.year,
                        datetime.month,
                        datetime.day,
                        datetime.hour,
                        datetime.minute,
                        datetime.second,
                        datetime.microsecond,
                        datetime.tzinfo)


def date_to_fakedate(date):
    """Add here a better docstring."""
    return FakeDate(date.year,
                    date.month,
                    date.day)


class FakeDate(with_metaclass(FakeDateMeta, real_date)):
    """Add here a better docstring."""
    
    dates_to_freeze = []
    tz_offsets = []

    def __new__(cls, *args, **kwargs):
        """Add here a better docstring."""
        return real_date.__new__(cls, *args, **kwargs)

    def __add__(self, other):
        result = real_date.__add__(self, other)
        if result is NotImplemented:
            return result
        return date_to_fakedate(result)

    def __sub__(self, other):
        result = real_date.__sub__(self, other)
        if result is NotImplemented:
            return result
        if isinstance(result, real_date):
            return date_to_fakedate(result)
        else:
            return result

    @classmethod
    def today(cls):
        """Add here a better docstring."""
        result = cls._now()
        return date_to_fakedate(result)


FakeDate.min = date_to_fakedate(real_date.min)
FakeDate.max = date_to_fakedate(real_date.max)


class FakeDatetimeMeta(FakeDateMeta):
    """Add here a better docstring."""
    
    @classmethod
    def __instancecheck__(self, obj):
        return isinstance(obj, real_datetime)


class FakeDatetime(with_metaclass(FakeDatetimeMeta, real_datetime,
                                  FakeDate)):
    """Add here a better docstring."""
    
    times_to_freeze = []
    tz_offsets = []

    def __new__(cls, *args, **kwargs):
        """Add here a better docstring."""
        return real_datetime.__new__(cls, *args, **kwargs)

    def __add__(self, other):
        result = real_datetime.__add__(self, other)
        if result is NotImplemented:
            return result
        return datetime_to_fakedatetime(result)

    def __sub__(self, other):
        result = real_datetime.__sub__(self, other)
        if result is NotImplemented:
            return result
        if isinstance(result, real_datetime):
            return datetime_to_fakedatetime(result)
        else:
            return result

    def astimezone(self, tz=None):
        """Add here a better docstring."""
        if tz is None:
            tz = tzlocal()
        return datetime_to_fakedatetime(
            real_datetime.astimezone(self, tz))

    @classmethod
    def now(cls, tz=None):
        """Add here a better docstring."""
        now = cls._now()
        if tz:
            result = tz.fromutc(now.replace(tzinfo=tz)) +\
                datetime.timedelta(hours=cls._tz_offset())
        else:
            result = now
        return datetime_to_fakedatetime(result)

    def date(self):
        """Add here a better docstring."""
        return date_to_fakedate(self)

    @classmethod
    def today(cls):
        """Add here a better docstring."""
        return cls.now(tz=None)

    @classmethod
    def utcnow(cls):
        """Add here a better docstring."""
        result = cls._now()
        return datetime_to_fakedatetime(result)


FakeDatetime.min = datetime_to_fakedatetime(real_datetime.min)
FakeDatetime.max = datetime_to_fakedatetime(real_datetime.max)


def pickle_fake_date(datetime_):
    """Pickle function for FakeDate."""
    return FakeDate, (
        datetime_.year,
        datetime_.month,
        datetime_.day,
    )


@staticmethod
def pickle_fake_datetime(datetime_):
    """Pickle function for FakeDatetime."""
    return FakeDatetime, (
        datetime_.year,
        datetime_.month,
        datetime_.day,
        datetime_.hour,
        datetime_.minute,
        datetime_.second,
        datetime_.microsecond,
        datetime_.tzinfo,
    )


class DatetimePatcher(BasicPatcher):
    """Patcher of the datetime module.
    
    patching:
        - datetime.today
        - datetime.now
        - datetime.utcnow
    """
    
    def __init__(self, *args, **kwargs):
        """Create the patch."""
        super(DatetimePatcher, self).__init__(*args, **kwargs)
        
        MockedDate._now = self._now
        MockedDatetime._now = self._now
        
        FakeDate._now = self._now
        FakeDatetime._now = self._now
        
    def start(self):
        """Start the patch of datetime.datetime class.
        
        This method overrides the method of the basic patcher.
        """
        datetime.datetime = FakeDatetime
        datetime.date = FakeDate
        
        copyreg.dispatch_table[real_datetime] = pickle_fake_datetime
        copyreg.dispatch_table[real_date] = pickle_fake_date
        
        to_patch = [
            ('real_date', real_date, 'FakeDate', FakeDate),
            ('real_datetime', real_datetime,
             'FakeDatetime', FakeDatetime),
        ]
        real_names = tuple(real_name for real_name, _, _, _ in to_patch)
        self.fake_names = tuple(fake_name for
                                real_name, _, fake_name, _ in to_patch)
        self.reals = dict((id(fake), real) for 
                          real_name, real, fake_name, fake in to_patch)
        fakes = dict((id(real), fake) for
                     real_name, real, fake_name, fake in to_patch)

        import sys
        
        # Save the current loaded modules
        self.modules_at_start = set(sys.modules.keys())

        for mod_name, module in list(sys.modules.items()):
            if mod_name is None or module is None:
                continue
            elif (not hasattr(module, "__name__") or
                  module.__name__ in ('datetime', 'time', 'datetime_patcher')):
                continue
            for module_attribute in dir(module):
                if module_attribute in real_names:
                    continue
                try:
                    attribute_value = getattr(module, module_attribute)
                except (ImportError, AttributeError, TypeError):
                    # For certain libraries, this can result in Error
                    continue
                fake = fakes.get(id(attribute_value))
                if fake:
                    setattr(module, module_attribute, fake)
    
    def _now(self):
        return real_datetime.fromtimestamp(self.clock.time)
