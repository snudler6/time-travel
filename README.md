[![Build Status](https://travis-ci.org/snudler6/time-travel.svg?branch=master)](https://travis-ci.org/snudler6/time-travel) [![Build status](https://ci.appveyor.com/api/projects/status/y13ewnvmj0muoapf/branch/master?svg=true)](https://ci.appveyor.com/project/snudler6/time-travel/branch/master)

# time-travel
python time libraries mocking

### time-travel is the coolest way to unit-test time sensetive modules.
### time-travel lets you write determenistic test for long and even infinite time scenarios.

**time-travel** supports python 2.7, 3.4, 3.5, 3.6 and pypy on both Linux and Windows.

## Quick start

### install

```pip install time_travel```

### Usage

`TimeTravel` is context manager patching all* time and I\O related modules in a 
single line. 

\* All modules currently patched :).

The initial time within the time travel context manager is set to 
86,400.0 seconds in order to support windows (this is the lowest acceptable 
value by the OS). This value is exported via ``time_travel.MIN_START_TIME``.

In order to improve TimeTravel's performance, you can give it the names of 
modules you want it to patch (in a list, tuple or a single name). 
If you want to patch the current module, you can use the local 
variable `__name__`.

# Links

[Full documentation](http://time-travel.readthedocs.io/en/latest/)

[PyPI project page](https://pypi.python.org/pypi/time_travel)
