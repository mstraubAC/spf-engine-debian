#!/usr/bin/env python

from distutils.core import setup
import os

DESC = """python-policyd-spf SPF Postfix policy server implemented in Python."""

setup(name='python-policyd-spf',
      version='0.8.0',
      description=DESC,
      author='Scott Kitterman',
      author_email='scott@kitterman.com',
      url='https://launchpad.net/pypolicyd-spf',
      py_modules=['policydspfsupp', 'policydspfuser'],
      keywords = ['Postfix','spf','email'],
      scripts = ['policyd-spf'],
      data_files=[(os.path.join('share', 'man', 'man1'),
          ['policyd-spf.1']), (os.path.join('share', 'man', 'man5'),
          ['policyd-spf.conf.5']), (os.path.join('../etc', 'python-policyd-spf'),
          ['policyd-spf.conf']), (os.path.join('share', 'man', 'man5'),
          ['policyd-spf.peruser.5'])],
      classifiers = [
	'Development Status :: 5 - Production/Stable',
	'Environment :: No Input/Output (Daemon)',
	'Intended Audience :: Developers',
	'License :: OSI Approved :: GNU General Public License (GPL)',
	'Natural Language :: English',
	'Operating System :: POSIX',
	'Programming Language :: Python',
	'Topic :: Communications :: Email :: Mail Transport Agents',
	'Topic :: Communications :: Email :: Filters',
	'Topic :: Software Development :: Libraries :: Python Modules'
      ]
)
