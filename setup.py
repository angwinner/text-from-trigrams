# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name="trigrams",
    description="Generates text in the style of a given text file.",
    version=0.1,
    author="Angela Winner",
    author_email="awinner@comcast.net",
    license='MIT',
    py_modules=['trigrams'],
    package_dir={'': 'src'},
    install_requires=[],
    extras_require={'test': ['pytest', 'pytest-xdist']},
    entry_points={
        'console_scripts': [
            "trigrams = trigrams:main"
        ]
    }
)