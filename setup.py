#!/usr/bin/env python

from distutils.core import setup
import os

setup(name='django-skipjack',
      version='1.0',
      description='Django and Skipjack payment gateway integration',
      author='Richard Bolt',
      author_email='richard@richardbolt.com',
      url='http://github.com/richardbolt/django-skipjack/tree/master',
      packages=['skipjack'],
      keywords=['django', 'Skipjack', 'payment'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Framework :: Django',
          'Topic :: Office/Business :: Financial',
      ],
      long_description=open(
          os.path.join(os.path.dirname(__file__), 'README.md'),
      ).read().strip(),
)
