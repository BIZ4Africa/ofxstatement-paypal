#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import find_packages
from distutils.core import setup

version = '2.1.1'
with open('README.md') as f:
    long_description = f.read()

setup(name='ofxstatement-paypal',
      version=version,
      author='Alexander Krasnukhin',
      author_email='the.malkolm@gmail.com',
      url='https://github.com/EtsBiz4africa/ofxstatement-paypal',
      description=('ofxstatement plugins for paypal'),
      long_description=open("README.md").read(),
      long_description_content_type='text/markdown',
      license='Apache License 2.0',
      keywords=['ofx', 'ofxstatement', 'paypal'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3',
          'Natural Language :: English',
          'Topic :: Office/Business :: Financial :: Accounting',
          'Topic :: Utilities',
          'Environment :: Console',
          'Operating System :: OS Independent'
      ],
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['ofxstatement', 'ofxstatement.plugins'],
      entry_points={
          'ofxstatement': ['paypal-ng = ofxstatement.plugins.paypal:PayPalPlugin']
      },
      install_requires=['ofxstatement'],
      test_suite='ofxstatement.plugins.tests',
      include_package_data=True,
      zip_safe=True
      )
