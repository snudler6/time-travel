[![Build Status](https://travis-ci.org/snudler6/time-travel.svg?branch=master)](https://travis-ci.org/snudler6/time-travel)

# time-travel
python time libraries mocking

### time-travel is the fun and easy way to unit-test time sensetive modules.
### time-travel lets you write determenistic test for long and even infinite time scenarios.

**time-travel** supports python 2.7, 3.4, 3.5, 3.6 and pypy on Linux and  python 2.7, 3.4, 3.5 and 3.6 on Windows

## Quick start

### install

```pip install time_travel```

### Usage

`TimeTravel` is context manager patching all* time and I\O related modules in a single line.

\* All modules currently patched :) .

In order to improve TimeTravel's performance, you can give it the names of modules you want to patch (in list, tuple or single name). If you want to patch the current module, you can use the local variable `__name__`.

# Links

[Full documentation](http://time-travel.readthedocs.io/en/latest/)
[PyPI project page](https://pypi.python.org/pypi/time_travel)
