from setuptools import setup

version = '1.0.0'

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
        'time_travel.patchers': [
            'datetime_patcher = src.time_travel.patchers.datetime_patcher:DatetimePatcher',
            'select_patcher = src.time_travel.patchers.select_patcher:SelectPatcher',
            'poll_patcher = src.time_travel.patchers.poll_patcher:PollPatcher',
            'time_patcher = src.time_travel.patchers.time_patcher:TimePatcher',
        ],
    }
)
