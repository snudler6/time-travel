from setuptools import setup
import select

version = '1.1.0'


PATCHERS = [
        'datetime_patcher = src.time_travel.patchers.datetime_patcher:DatetimePatcher',
        'select_patcher = src.time_travel.patchers.select_patcher:SelectPatcher',
        'time_patcher = src.time_travel.patchers.time_patcher:TimePatcher',
    ]


if hasattr(select, 'poll'):
    PATCHERS.append('poll_patcher = src.time_travel.patchers.poll_patcher:PollPatcher')


setup(
    name='time_travel',
    version=version,
    description='Python time mocking',
    license='MIT',
    author='Shachar Nudler',
    author_email='snudler6@gmail.com',
    url='https://github.com/snudler6/time-travel',
    packages=('time_travel',),
    package_dir={'': 'src'},
    entry_points={
        'time_travel.patchers': PATCHERS,
    }
)
