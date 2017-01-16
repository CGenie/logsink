import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = "logsink",
    version = "0.0.4",
    author = "Przemyslaw Kaminski",
    author_email = "cgenie@gmail.com",
    description = ("Log sink client library"),
    license = "BSD",
    keywords = "logsink",
    url = "http://packages.python.org/an_example_pypi_project",
    install_requires=['requests==2.12.4'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
