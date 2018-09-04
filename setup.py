from setuptools import setup, find_packages
import select


version = '1.1.2'


patchers = [
    'datetime_patcher = time_travel.patchers.datetime_patcher:DatetimePatcher',
    'select_patcher = time_travel.patchers.select_patcher:SelectPatcher',
    'time_patcher = time_travel.patchers.time_patcher:TimePatcher',
]


if hasattr(select, 'poll'):
    patchers.append('poll_patcher = time_travel.patchers.poll_patcher:PollPatcher')


setup(
    name='time_travel',
    version=version,
    description='Python time mocking',
    long_description=open('README.rst').read(),
    license='MIT',
    author='Shachar Nudler',
    author_email='snudler6@gmail.com',
    url='https://github.com/snudler6/time-travel',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Testing',
    ],
    packages=find_packages('src', exclude=["tests*"]),
    package_dir={'': 'src'},
    entry_points={
        'time_travel.patchers': patchers,
    }
)
