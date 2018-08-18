"""A patch to the datetime module."""

from .base_patcher import BasePatcher

import sys
import datetime

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


def date_to_fakedate(date):
    """Return mocked datetime object from original one."""
    return FakeDate(date.year,
                    date.month,
                    date.day)


def datetime_to_fakedatetime(datetime):
    """Return mocked datetime object from original one."""
    return FakeDatetime(datetime.year,
                        datetime.month,
                        datetime.day,
                        datetime.hour,
                        datetime.minute,
                        datetime.second,
                        datetime.microsecond,
                        datetime.tzinfo)


class FakeDate(with_metaclass(DateSubclassMeta, 'date', _real_date)):
    """Mocked datetime.date class."""

    def __new__(cls, *args, **kwargs):
        """Return a new mocked date object."""
        return _real_date.__new__(cls, *args, **kwargs)

    @classmethod
    def today(cls):
        """Return today's date."""
        result = cls._now()
        return date_to_fakedate(result)


FakeDate.min = date_to_fakedate(_real_date.min)
FakeDate.max = date_to_fakedate(_real_date.max)


class FakeDatetime(with_metaclass(DatetimeSubclassMeta, 'datetime',
                                  _real_datetime, FakeDate)):
    """Mocked datetime.datetime class."""

    def __new__(cls, *args, **kwargs):
        """Return a new mocked datetime object."""
        return _real_datetime.__new__(cls, *args, **kwargs)

    @classmethod
    def now(cls, tz=None):
        """Return a datetime object representing current time."""
        now = cls._now()
        if tz:
            result = tz.fromutc(now.replace(tzinfo=tz)) +\
                datetime.timedelta(hours=cls._tz_offset())
        else:
            result = now
        return datetime_to_fakedatetime(result)

    @classmethod
    def today(cls):
        """Return a datetime object representing current time."""
        return cls.now(tz=None)

    @classmethod
    def utcnow(cls):
        """Return a datetime object representing current time."""
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


class DatetimePatcher(BasePatcher):
    """Patcher of the datetime module.

    patching:
        - datetime.today
        - datetime.now
        - datetime.utcnow
        - date.today
    """

    def __init__(self, **kwargs):
        """Create the patcher."""
        super(DatetimePatcher, self).__init__(patcher_module=__name__,
                                              **kwargs)

        FakeDate._now = self._now
        FakeDatetime._now = self._now

    def get_patched_module(self):
        """Return the actual module obect to be patched."""
        return datetime

    def get_patch_actions(self):
        """Return list of the patches to do."""
        return [
            ('date', _real_date, FakeDate),
            ('datetime', _real_datetime, FakeDatetime)
        ]

    def start(self):
        """Change pickle function for datetime to handle mocked datetime."""
        super(DatetimePatcher, self).start()

        copyreg.dispatch_table[_real_datetime] = pickle_fake_datetime
        copyreg.dispatch_table[_real_date] = pickle_fake_date

    def stop(self):
        """Return pickle behavior to normal."""
        copyreg.dispatch_table.pop(_real_datetime)
        copyreg.dispatch_table.pop(_real_date)

        super(DatetimePatcher, self).stop()

    def _now(self):
        return _real_datetime.fromtimestamp(self.clock.time)
