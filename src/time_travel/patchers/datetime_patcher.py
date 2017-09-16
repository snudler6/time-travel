"""A patch to the datetime module."""

from .basic_patcher import BasicPatcher

import sys
import mock
import datetime
from dateutil.tz import tzlocal

try:
    import copy_reg as copyreg
except ImportError:
    import copyreg


_real_datetime = datetime.datetime
_real_date = datetime.date


def with_metaclass(meta, name, *bases):
    """Create a base class with a metaclass."""
    return meta(name, bases, {})
    

class DateSubclassMeta(type):
    """Date mock metaclass to check instancechek to the real class."""
    
    @classmethod
    def __instancecheck__(mcs, obj):
        return isinstance(obj, _real_date)


class DatetimeSubclassMeta(DateSubclassMeta):
    """Datetime mock metaclass to check instancechek to the real class."""
    
    @classmethod
    def __instancecheck__(mcs, obj):
        return isinstance(obj, _real_datetime)


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


class FakeDate(with_metaclass(DateSubclassMeta, 'date', _real_date)):
    """Add here a better docstring."""
    
    dates_to_freeze = []
    tz_offsets = []

    def __new__(cls, *args, **kwargs):
        """Add here a better docstring."""
        return _real_date.__new__(cls, *args, **kwargs)

    def __add__(self, other):
        result = _real_date.__add__(self, other)
        if result is NotImplemented:
            return result
        return date_to_fakedate(result)

    def __sub__(self, other):
        result = _real_date.__sub__(self, other)
        if result is NotImplemented:
            return result
        if isinstance(result, _real_date):
            return date_to_fakedate(result)
        else:
            return result

    @classmethod
    def today(cls):
        """Add here a better docstring."""
        result = cls._now()
        return date_to_fakedate(result)


FakeDate.min = date_to_fakedate(_real_date.min)
FakeDate.max = date_to_fakedate(_real_date.max)


class FakeDatetime(with_metaclass(DatetimeSubclassMeta, 'datetime',
                                  _real_datetime, FakeDate)):
    """Add here a better docstring."""
    
    times_to_freeze = []
    tz_offsets = []

    def __new__(cls, *args, **kwargs):
        """Add here a better docstring."""
        return _real_datetime.__new__(cls, *args, **kwargs)

    def __add__(self, other):
        result = _real_datetime.__add__(self, other)
        if result is NotImplemented:
            return result
        return datetime_to_fakedatetime(result)

    def __sub__(self, other):
        result = _real_datetime.__sub__(self, other)
        if result is NotImplemented:
            return result
        if isinstance(result, _real_datetime):
            return datetime_to_fakedatetime(result)
        else:
            return result

    def astimezone(self, tz=None):
        """Add here a better docstring."""
        if tz is None:
            tz = tzlocal()
        return datetime_to_fakedatetime(
            _real_datetime.astimezone(self, tz))

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


FakeDatetime.min = datetime_to_fakedatetime(_real_datetime.min)
FakeDatetime.max = datetime_to_fakedatetime(_real_datetime.max)


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
    
    def __init__(self, name=None, **kwargs):
        """Create the patch."""
        super(DatetimePatcher, self).__init__(**kwargs)
        
        FakeDate._now = self._now
        FakeDatetime._now = self._now
        
        self.patched_module = name
        
        self.patches = []
        #         if name is not None:
        #             self.patches.append(mock.patch(name + '.datetime',
        #                                            FakeDatetime))
        
    def start(self):
        """Start the patch of datetime.datetime class.
        
        This method overrides the method of the basic patcher.
        """
        for patch in self.patches:
            patch.start()
        
        datetime.datetime = FakeDatetime
        datetime.date = FakeDate
        
        copyreg.dispatch_table[_real_datetime] = pickle_fake_datetime
        copyreg.dispatch_table[_real_date] = pickle_fake_date
        
        to_patch = [
            # (local_name, orig_local_class, fake_name, fake_class)
            ('_real_date', _real_date, 'FakeDate', FakeDate),
            ('_real_datetime', _real_datetime, 'FakeDatetime', FakeDatetime),
        ]
        
        local_names = tuple(real_name for real_name, _, _, _ in to_patch)
        self.fake_names = tuple(fake_name for _, _, fake_name, _ in to_patch)
        self.reals = {id(fake): real for _, real, _, fake in to_patch}
        fakes = {id(real): fake for _, real, _, fake in to_patch}
        real_ids = [id(real) for _, real, _, _ in to_patch]

        # Save the current loaded modules
        self.modules_at_start = set(sys.modules.keys())
        
        modules = [
            module for mod_name, module in sys.modules.items() if
            mod_name is not None and module is not None and
            hasattr(module, '__name__') and
            module.__name__ not in ('datetime', 'datetime_patcher') and
            (self.patched_module is None or
             module.__name__ == self.patched_module)
        ]
        
        for module in modules:
            attrs = [attr for attr in dir(module) if
                     hasattr(module, attr) and
                     attr not in local_names and
                     id(getattr(module, attr)) in real_ids]
            for module_attribute in attrs:
                # try:
                #     attribute_value = getattr(module, module_attribute)
                # except (ImportError, AttributeError, TypeError):
                #     # For certain libraries, this can result in Error
                #     continue
                attribute_value = getattr(module, module_attribute)
                fake = fakes.get(id(attribute_value))
                setattr(module, module_attribute, fake)
                
    def _now(self):
        return _real_datetime.fromtimestamp(self.clock.time)
