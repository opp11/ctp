from setuptools import setup
from ctp import __author__, __version__

with open('LICENSE') as f:
    license = f.read()

with open('README.md') as f:
    readme = f.read()

setup(
    name='ctp',
    version=__version__,
    author=__author__,
    author_email='patrick.opp@hotmail.com',
    description='Python script for compiling test protocols',
    long_description=readme,
    license=license,
    url='https://github.com/opp11/ctp'
)