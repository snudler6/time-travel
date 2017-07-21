from setuptools import setup

version = '0.1.2'

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
)
