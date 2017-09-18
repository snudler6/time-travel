"""A patch to the datetime module.

This patcher is based on the work done by: spulec/freezegun under
https://github.com/spulec/freezegun

Copyright (C) 2017 spulec/freezegun

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.

Modifications:

Modifications to the file was to leave the patching of datetime libray only,
and remove any other patching or any other advanced logic.
"""

from .basic_patcher import BasicPatcher

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
        - date.today
    """
    
    def __init__(self, patched_modules=None, **kwargs):
        """Create the patch."""
        super(DatetimePatcher, self).__init__(**kwargs)
        
        FakeDate._now = self._now
        FakeDatetime._now = self._now
        
        if patched_modules is None:
            self.patched_modules = []
        elif isinstance(patched_modules, (list, tuple)):
            self.patched_modules = patched_modules
        else:
            self.patched_modules = [patched_modules]
        
        self._undo_set = set()
        
    def start(self):
        """Start the patch of datetime.datetime class.
        
        This method overrides the method of the basic patcher.
        """
        datetime.datetime = FakeDatetime
        datetime.date = FakeDate
        
        copyreg.dispatch_table[_real_datetime] = pickle_fake_datetime
        copyreg.dispatch_table[_real_date] = pickle_fake_date
        
        to_patch = (
            # (local_name, orig_local_class, fake_name, fake_class)
            ('_real_date', _real_date, 'FakeDate', FakeDate),
            ('_real_datetime', _real_datetime, 'FakeDatetime', FakeDatetime),
        )
        
        local_names = tuple(real_name for real_name, _, _, _ in to_patch)
        real_id_to_fake = {id(real): fake for _, real, _, fake in to_patch}

        modules = [sys.modules[name] for name in self.patched_modules] if \
            self.patched_modules else [
                module for mod_name, module in sys.modules.items() if
                mod_name is not None and module is not None and
                hasattr(module, '__name__') and
                module.__name__ not in ('datetime', 'datetime_patcher') 
        ]
        
        for module in modules:
            for attr in dir(module):
                try:
                    attribute_value = getattr(module, attr)
                except (ValueError, AttributeError, ImportError):
                    # For some libraries, this happen.
                    continue
                
                if attr in local_names or\
                        id(attribute_value) not in real_id_to_fake.keys():
                    continue
                    
                fake = real_id_to_fake.get(id(attribute_value))
                setattr(module, attr, fake)
                self._save_for_undo(module, attr, attribute_value)
                
    def stop(self):
        """Stop the patching of datetime module."""
        datetime.date = _real_date
        datetime.datetime = _real_datetime
        
        for module, attribute, original_value in self._undo_set:
            setattr(module, attribute, original_value)
            
        self._undo_set = set()
        
        copyreg.dispatch_table.pop(_real_datetime)
        copyreg.dispatch_table.pop(_real_date)
                
    def _save_for_undo(self, module, attribute, original_value):
        self._undo_set.add((module, attribute, original_value))
    
    def _now(self):
        return _real_datetime.fromtimestamp(self.clock.time)
