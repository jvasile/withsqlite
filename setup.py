#!/usr/bin/env python
from distutils.core import setup


setup(
    name='withsqlite',
    version='0.1',
    author='James Vasile',
    #author_email='TBC',
    url='http://github.com/jvasile/withsqlite',
    long_description=open('README.mdwn').read(),
    py_modules=['withsqlite'],
    license="GPL-3",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPL-3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)
