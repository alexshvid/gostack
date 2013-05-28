#!/usr/bin/python

import osutils

osutils.beroot()

osutils.run_std('apt-get install -y nova-objectstore')

