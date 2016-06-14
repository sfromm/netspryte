#!/usr/bin/python

import os
import sys

sys.path.insert(0, os.path.abspath('lib'))
from snmpryte import __version__, __author__, __email__

try:
    from setuptools import setup, find_packages
except ImportError:
    print("snmpryte needs setuptools to build")
    sys.exit(1)

setup(name='snmpryte',
      version=__version__,
      author=__author__,
      author_email=__email__,
      license='GPLv3',
      install_requires=['pysnmp'],
      package_dir={'' : 'lib'},
      packages=find_packages('lib'),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Natural Language :: English',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: System :: Systems Administration',
          'Topic :: System :: Monitoring',
          'Topic :: System :: Networking',
          'Topic :: Utilities',
      ],
      scripts=[
          'bin/rrd-add-ds',
          'bin/snmpryte-collect-snmp',
          'bin/snmpryte-mk-graphs',
          'bin/snmpryte-discover',
      ],
      data_files=[])
