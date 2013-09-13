#!/usr/bin/env python
from distutils.core import setup, Command


class TestRunner(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys
        import subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

setup(
    name='withsqlite',
    version='0.1',
    author='James Vasile',
    #author_email='TBC',
    url='http://github.com/jvasile/withsqlite',
    long_description=open('README.mdwn').read(),
    py_modules=['withsqlite'],
    cmdclass={'test': TestRunner},
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
