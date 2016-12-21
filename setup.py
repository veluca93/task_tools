import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "italianformat",
    version = "0.0.1",
    author = "Luca Versari",
    author_email = "veluca93@gmail.com",
    description = ("Tools for the new italian task format."),
    license = "GPLv3",
    keywords = "ioi programming contest",
    url = "https://github.com/veluca93/task_tools",
    packages=['italianformat'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    entry_points={
        "console_scripts": [
                "itaMake=italianformat:main"
            ]
    }
)

