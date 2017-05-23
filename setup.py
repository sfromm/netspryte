#!/usr/bin/python

import os
import sys

sys.path.insert(0, os.path.abspath('lib'))
from netspryte import __version__, __author__, __email__

try:
    from setuptools import setup, find_packages
except ImportError:
    print("netspryte needs setuptools to build")
    sys.exit(1)

def get_file_list(base):
    paths = list()
    for root, dirs, files in os.walk(base):
        for path in files:
            reldir = os.path.relpath(root, base)
            paths.append(os.path.join(base, reldir, path))
    return paths

setup(name='netspryte',
      version=__version__,
      author=__author__,
      author_email=__email__,
      license='GPLv3',
      install_requires=[
          'Flask',
          'peewee',
          'psycopg2',
          'pysnmp',
          'python-crontab',
          'rrdtool',
          ],
      package_dir={'' : 'lib'},
      packages=find_packages('lib'),
      include_package_data=True,
      zip_safe=False,
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
          'bin/netspryte-collect-snmp',
          'bin/netspryte-discover',
          'bin/netspryte-gen-graph.cgi',
          'bin/netspryte-mk-html',
          'bin/netspryte-janitor',
          'bin/netspryte-tag',
          'bin/rrd-add-ds',
          'bin/rrd-merge-rrd',
          'bin/rrd-tune',
          'bin/rrd-remove-spikes',
      ],
      data_files=[
          ('etc/netspryte', ['etc/netspryte.cfg']),
          ('etc/cron.d', ['etc/netspryte.cron']),
          ('share/netspryte/www', ['web/hello.py']),
          ('share/netspryte/www/', ['web/uwsgi.ini']),
          ('share/netspryte/www/static/css', get_file_list('web/static/css')),
          ('share/netspryte/www/static/images', get_file_list('web/static/images')),
          ('share/netspryte/www/static/js', get_file_list('web/static/js')),
          ('share/netspryte/www/templates', get_file_list('web/templates')),
      ]
)
